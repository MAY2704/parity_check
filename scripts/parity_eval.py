#!/usr/bin/env python3
"""ParityKit deterministic parity harness.

Executes the core of the `parity-evaluation` skill (v3.x) as re-runnable
arithmetic instead of model-followed prose:

  1. Executes the artifact under test via its module harness
     (input/artifacts/{module}/harness.mjs, run through scripts/run_artifact.mjs).
  2. Normalizes all sides per the rule's declared rounding/tolerance.
  3. Dual-compares against both oracles: golden dataset (empirical) and
     rule-engine formula (analytical), field-per-case.
  4. Runs differential fuzzing + boundary cases against the rule engine.
  5. Runs declared metamorphic property checks against the artifact.
  6. Scores golden-dataset adequacy (volume, range, boundary, provenance).
  7. Computes TP/FP/FN/TN and precision/recall/accuracy/F1 under the
     conventions in skills/parity-evaluation/REFERENCE.md, including the
     degenerate-case rules (metrics are null when undefined, never 1.0).
  8. Emits one skill message conforming to
     context/schemas/skill-message.schema.json.

Usage (from repo root):

    python scripts/parity_eval.py <module> [--fuzz N] [--seed S]
        [--artifact-output FILE] [--out FILE] [--run-id ID]

Exit codes: 0 pass/partial, 1 fail, 2 blocked (missing input or artifact
execution failure — fail-closed, never silently skipped).

The LLM-facing skill (skills/parity-evaluation/SKILL.md) orchestrates and
interprets this script's message; it does not re-derive any number in it.
"""

from __future__ import annotations

import argparse
import ast
import json
import operator
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Confidence formula constants — documented in skills/parity-evaluation/REFERENCE.md.
# Change them there and here together (that is a MAJOR bump).
CONF_ORACLE_WEIGHT = 0.50
CONF_ADEQUACY_WEIGHT = 0.25
CONF_FUZZ_WEIGHT = 0.25
CONF_CAP = 0.95
FUZZ_FULL_CREDIT_CASES = 100

ADEQ_W_VOLUME = 0.25
ADEQ_W_RANGE = 0.35
ADEQ_W_BOUNDARY = 0.25
ADEQ_W_PROVENANCE = 0.15
DEFAULT_TARGET_CASE_COUNT = 50
PROVENANCE_FACTOR = {"production": 1.0, "mixed": 0.7, "synthetic": 0.3}

DIVERGENCE_EXAMPLE_LIMIT = 10


# ---------------------------------------------------------------------------
# Safe formula evaluation (the analytical oracle)
# ---------------------------------------------------------------------------

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCS = {"min": min, "max": max, "abs": abs}


def eval_formula(expr: str, variables: dict) -> float:
    """Evaluate an arithmetic rule-engine formula over named inputs.

    Whitelisted AST only: numbers, input names, + - * / ** %, unary +/-,
    and min/max/abs. Anything else is a hard error, not a guess.
    """
    tree = ast.parse(expr, mode="eval")

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id not in variables:
                raise ValueError(f"formula references undeclared input '{node.id}'")
            return variables[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            return _BIN_OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](walk(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
            return _FUNCS[node.func.id](*[walk(a) for a in node.args])
        raise ValueError(f"disallowed construct in formula: {ast.dump(node)}")

    return float(walk(tree))


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

_ROUNDING_MODES = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}


def normalize_value(value, rounding: dict):
    """Round a numeric value per the rule's declared rounding. Non-numeric or
    missing values pass through unchanged (comparison then flags them)."""
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    if not rounding:
        return float(value)
    dp = int(rounding.get("decimal_places", 2))
    mode = _ROUNDING_MODES.get(rounding.get("mode", "half_up"))
    if mode is None:
        raise ValueError(f"unknown rounding mode: {rounding.get('mode')}")
    quantum = Decimal(1).scaleb(-dp)
    return float(Decimal(repr(float(value))).quantize(quantum, rounding=mode))


def default_tolerance(rounding: dict) -> float:
    """Half of one unit in the last rounded place; 0 when the rule declares
    no rounding (tolerance: 0 means exact comparison)."""
    if not rounding:
        return 0.0
    return 0.5 * 10 ** (-int(rounding.get("decimal_places", 2)))


def values_match(a, b, tolerance: float) -> bool:
    if a is None or b is None:
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) <= tolerance + 1e-12
    return a == b


# ---------------------------------------------------------------------------
# Rule config / golden dataset loading
# ---------------------------------------------------------------------------

def load_rule_config(module: str) -> dict | None:
    path = ROOT / "context" / "rules-engine" / f"{module}.rules.yaml"
    if not path.exists():
        return None
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    cfg["_path"] = str(path.relative_to(ROOT))
    return cfg


def load_golden(module: str) -> dict | None:
    path = ROOT / "context" / "golden-datasets" / module / "golden.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_path"] = str(path.relative_to(ROOT))
    return data


def load_review(module: str) -> dict:
    """Optional human review file reclassifying flagged discrepancies and
    recording escaped defects. See parity-evaluation/REFERENCE.md."""
    path = ROOT / "context" / "golden-datasets" / module / "review.json"
    if not path.exists():
        return {"reclassifications": {}, "escaped_defects": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("reclassifications", {})
    data.setdefault("escaped_defects", [])
    return data


def output_specs(cfg: dict) -> list:
    """Declared output fields: name, golden_field, per-field tolerance."""
    rounding = cfg.get("rounding") or {}
    specs = []
    for spec in cfg.get("output_fields", []):
        specs.append({
            "name": spec["name"],
            "golden_field": spec.get("golden_field", f"expected_{spec['name']}"),
            "tolerance": float(spec.get("tolerance", default_tolerance(rounding))),
        })
    return specs


def formula_for(cfg: dict, field: str) -> str | None:
    formulas = cfg.get("formulas")
    if formulas:
        return formulas.get(field)
    if cfg.get("formula") and cfg["output_fields"][0]["name"] == field:
        return cfg["formula"]
    return None


# ---------------------------------------------------------------------------
# Artifact execution
# ---------------------------------------------------------------------------

def run_artifact(module: str, cases: list) -> list:
    """Execute the artifact's harness once over all cases. Raises on any
    failure — a half-executed artifact is a blocked run, not a partial pass."""
    harness = ROOT / "input" / "artifacts" / module / "harness.mjs"
    if not harness.exists():
        raise FileNotFoundError(
            f"no execution harness at {harness.relative_to(ROOT)}; "
            "add one (see input/README.md) or pass --artifact-output"
        )
    node = shutil.which("node")
    if node is None:
        raise FileNotFoundError("node not found on PATH; needed to execute the artifact harness")
    cmd = [node]
    version = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    try:
        major, minor = (int(p) for p in version.lstrip("v").split(".")[:2])
        # native TS type-stripping: default from 23.6, behind a flag on 22.6+
        if major == 22 and minor >= 6:
            cmd.append("--experimental-strip-types")
    except ValueError:
        pass
    proc = subprocess.run(
        cmd + [str(ROOT / "scripts" / "run_artifact.mjs"), str(harness)],
        input=json.dumps(cases),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"artifact harness failed (exit {proc.returncode}): {proc.stderr.strip()}")
    outputs = json.loads(proc.stdout)
    if len(outputs) != len(cases):
        raise RuntimeError(f"harness returned {len(outputs)} outputs for {len(cases)} cases")
    return outputs


# ---------------------------------------------------------------------------
# Case generation: boundaries + fuzz
# ---------------------------------------------------------------------------

def domain_for(cfg: dict, golden_cases: list, name: str, gaps: list) -> dict | None:
    declared = (cfg.get("input_domains") or {}).get(name)
    if declared is not None:
        return declared
    observed = [c[name] for c in golden_cases if isinstance(c.get(name), (int, float))]
    if observed:
        gaps.append(
            f"input '{name}' has no declared input_domain; fuzz/boundary generation "
            "fell back to the observed golden-dataset range, which cannot probe beyond it"
        )
        return {"min": min(observed), "max": max(observed)}
    return None


def random_value(rng: random.Random, dom: dict):
    lo, hi = float(dom["min"]), float(dom["max"])
    if dom.get("integer"):
        return rng.randint(int(lo), int(hi))
    return round(rng.uniform(lo, hi), 6)


def random_case(rng: random.Random, domains: dict) -> dict:
    return {name: random_value(rng, dom) for name, dom in domains.items()}


def boundary_values_for(dom: dict) -> list:
    lo, hi = float(dom["min"]), float(dom["max"])
    values = {lo, hi, (lo + hi) / 2}
    values.update(float(v) for v in dom.get("boundary_values", []))
    if dom.get("integer"):
        values = {int(v) for v in values}
    return sorted(values)


def generate_boundary_cases(rng: random.Random, domains: dict, fills_per_value: int = 3) -> list:
    """For every boundary value of every input, pin that input and fill the
    rest randomly, several times. Deduplicated."""
    cases, seen = [], set()
    for name, dom in domains.items():
        for value in boundary_values_for(dom):
            for _ in range(fills_per_value):
                case = random_case(rng, domains)
                case[name] = value
                key = tuple(sorted(case.items()))
                if key not in seen:
                    seen.add(key)
                    cases.append(case)
    return cases


# ---------------------------------------------------------------------------
# Metamorphic property checks
# ---------------------------------------------------------------------------

def build_property_probes(cfg: dict, domains: dict, rng: random.Random) -> list:
    """Build executable probes for each declared property. Each probe is a
    dict with the cases to run and a `check(outputs) -> violations` closure
    operating on the artifact's outputs for those cases."""
    probes = []
    specs = output_specs(cfg)
    if not specs or not domains:
        return probes
    field = specs[0]["name"]
    tol = specs[0]["tolerance"]

    for prop in cfg.get("properties", []):
        ptype = prop.get("type")

        if ptype == "monotonic_nondecreasing":
            over = prop["over"]
            if over not in domains:
                continue
            cases, runs = [], []
            for _ in range(5):
                fill = random_case(rng, domains)
                sweep = sorted({random_value(rng, domains[over]) for _ in range(10)}
                               | {domains[over]["min"], domains[over]["max"]},
                               key=float)
                start = len(cases)
                for v in sweep:
                    cases.append({**fill, over: v})
                runs.append((start, len(cases), sweep, fill))

            def check_mono(outputs, runs=runs, over=over, field=field, tol=tol):
                violations = []
                for start, end, sweep, fill in runs:
                    vals = [outputs[i].get(field) for i in range(start, end)]
                    for j in range(1, len(vals)):
                        if vals[j] is None or vals[j - 1] is None:
                            continue
                        if vals[j] < vals[j - 1] - tol:
                            violations.append({
                                "inputs": {k: v for k, v in fill.items() if k != over},
                                over: [sweep[j - 1], sweep[j]],
                                field: [vals[j - 1], vals[j]],
                            })
                            break
                return violations

            probes.append({"type": ptype, "over": over, "cases": cases, "check": check_mono})

        elif ptype == "linear_in":
            over = prop["over"]
            if over not in domains:
                continue
            dom = domains[over]
            lo, hi = float(dom["min"]), float(dom["max"])
            cases, pairs = [], []
            for _ in range(8):
                k = rng.choice([2, 3, 5])
                base = random_case(rng, domains)
                # keep both x and k*x inside the domain, away from zero
                x = rng.uniform(max(lo, hi / (20 * k)), hi / k)
                if dom.get("integer"):
                    x = max(1, int(x))
                base_case = {**base, over: x}
                scaled_case = {**base, over: (x * k if not dom.get("integer") else int(x) * k)}
                pairs.append((len(cases), len(cases) + 1, k))
                cases.extend([base_case, scaled_case])

            def check_linear(outputs, pairs=pairs, cases=cases, field=field, tol=tol, over=over):
                violations = []
                for i_base, i_scaled, k in pairs:
                    f_x, f_kx = outputs[i_base].get(field), outputs[i_scaled].get(field)
                    if f_x is None or f_kx is None:
                        continue
                    # rounding on each evaluation can contribute up to one
                    # tolerance each, and the scaled side is amplified by k
                    if abs(f_kx - k * f_x) > tol * (k + 1):
                        violations.append({
                            "inputs": {kk: v for kk, v in cases[i_base].items() if kk != over},
                            over: [cases[i_base][over], cases[i_scaled][over]],
                            "expected_ratio": k,
                            field: [f_x, f_kx],
                        })
                return violations

            probes.append({"type": ptype, "over": over, "cases": cases, "check": check_linear})

        elif ptype == "zero_when":
            pinned, value = prop["input"], prop["value"]
            cases = []
            for _ in range(8):
                case = random_case(rng, domains)
                case[pinned] = value
                cases.append(case)

            def check_zero(outputs, cases=cases, field=field, tol=tol):
                violations = []
                for i, out in enumerate(outputs):
                    v = out.get(field)
                    if v is not None and abs(v) > tol:
                        violations.append({"inputs": cases[i], field: v})
                return violations

            probes.append({"type": ptype, "over": pinned, "cases": cases, "check": check_zero})

        else:
            probes.append({"type": ptype, "over": prop.get("over"), "cases": [],
                           "check": None, "error": f"unknown property type '{ptype}'"})
    return probes


# ---------------------------------------------------------------------------
# Golden-dataset adequacy
# ---------------------------------------------------------------------------

def score_adequacy(cfg: dict, golden: dict, domains: dict, gaps: list) -> dict:
    cases = golden.get("cases", [])
    target = int((cfg.get("adequacy") or {}).get("target_case_count", DEFAULT_TARGET_CASE_COUNT))
    volume = min(1.0, len(cases) / target) if target > 0 else 1.0

    range_scores, boundary_scores = [], []
    for name, dom in domains.items():
        lo, hi = float(dom["min"]), float(dom["max"])
        span = hi - lo
        observed = [float(c[name]) for c in cases if isinstance(c.get(name), (int, float))]
        if span <= 0 or not observed:
            range_scores.append(0.0)
        else:
            range_scores.append(max(0.0, min(1.0, (max(observed) - min(observed)) / span)))
        bvals = boundary_values_for(dom)
        if bvals:
            eps = max(1e-9, 0.005 * span)
            hit = sum(1 for b in bvals if any(abs(float(b) - o) <= eps for o in observed))
            boundary_scores.append(hit / len(bvals))
    range_coverage = sum(range_scores) / len(range_scores) if range_scores else 0.0
    boundary_coverage = sum(boundary_scores) / len(boundary_scores) if boundary_scores else 0.0

    provenance = golden.get("provenance")
    if provenance not in PROVENANCE_FACTOR:
        gaps.append("golden dataset declares no provenance (production/mixed/synthetic); "
                    "scored 0 for the provenance component until declared")
        provenance_factor = 0.0
    else:
        provenance_factor = PROVENANCE_FACTOR[provenance]

    score = (ADEQ_W_VOLUME * volume + ADEQ_W_RANGE * range_coverage
             + ADEQ_W_BOUNDARY * boundary_coverage + ADEQ_W_PROVENANCE * provenance_factor)
    return {
        "case_count": len(cases),
        "target_case_count": target,
        "volume": round(volume, 4),
        "range_coverage": round(range_coverage, 4),
        "boundary_coverage": round(boundary_coverage, 4),
        "provenance": provenance or "undeclared",
        "provenance_factor": provenance_factor,
        "score": round(score, 4),
    }


# ---------------------------------------------------------------------------
# Metrics (conventions per skills/parity-evaluation/REFERENCE.md v3)
# ---------------------------------------------------------------------------

def compute_metrics(discrepancies: list, matched_units: int, uncovered_units: int,
                    escaped_defects: list) -> dict:
    """Field-per-case confusion matrix with explicit degenerate handling.

    Flagged discrepancies are provisional TPs unless a human review has
    reclassified them (fail-closed). Uncovered units and recorded escaped
    defects are FNs. A ratio whose denominator is zero is null, never 1.0.
    """
    tp = sum(1 for d in discrepancies if d["classification"] not in
             ("tolerance-acceptable", "legacy-defect-now-fixed"))
    fp = len(discrepancies) - tp
    fn = uncovered_units + len(escaped_defects)
    tn = matched_units
    total = tp + fp + fn + tn

    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    accuracy = (tp + tn) / total if total > 0 else None
    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = None

    compared = tp + fp + tn
    notes = []
    if precision is None:
        notes.append("precision undefined: nothing was flagged (TP+FP=0)")
    if recall is None:
        notes.append("recall undefined: no known or presumed defects (TP+FN=0)")
    if f1 is None:
        notes.append("f1 undefined: see precision/recall; downstream scoring must use "
                     "the null-metric fallback, not substitute 1.0")

    return {
        "unit_of_analysis": "field-per-case",
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "comparison_units": total,
        "match_rate": round(tn / compared, 4) if compared > 0 else None,
        "oracle_coverage": round((total - uncovered_units) / total, 4) if total > 0 else None,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "degenerate_notes": notes,
    }


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------

def evaluate(module: str, fuzz_n: int, seed: int, artifact_output_file: str | None,
             run_id: str | None) -> tuple[dict, int]:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = run_id or f"run-{now.isoformat().replace('+00:00', 'Z')}-{module}"
    gaps: list = []

    def message(status, confidence, result, exit_code, evidence=None):
        return {
            "skill": "parity-evaluation",
            "skill_version": "3.0.0",
            "module": module,
            "run_id": run_id,
            "timestamp": now.isoformat().replace("+00:00", "Z"),
            "status": status,
            "confidence": confidence,
            "result": result,
            "evidence_refs": evidence or [],
            "gaps": gaps,
        }, exit_code

    blocked_conf = {"value": 0.0, "band": "low", "source": "calibrated",
                    "basis": "Run blocked before comparison; no evidence produced."}

    cfg = load_rule_config(module)
    golden = load_golden(module)
    if golden is None or not golden.get("cases"):
        gaps.append(f"no golden dataset at context/golden-datasets/{module}/golden.json")
        return message("blocked", blocked_conf, {"error": "missing golden dataset"}, 2)
    if cfg is None:
        gaps.append(f"no rule config at context/rules-engine/{module}.rules.yaml; "
                    "the analytical oracle, fuzzing, and property checks all need it")
        return message("blocked", blocked_conf, {"error": "missing rule config"}, 2)
    specs = output_specs(cfg)
    if not specs:
        gaps.append("rule config declares no output_fields; nothing to compare")
        return message("blocked", blocked_conf, {"error": "no output_fields declared"}, 2)

    rounding = cfg.get("rounding") or {}
    inputs = cfg.get("inputs", [])
    golden_cases = golden["cases"]
    rng = random.Random(seed)

    domains = {}
    for name in inputs:
        dom = domain_for(cfg, golden_cases, name, gaps)
        if dom is not None:
            domains[name] = dom

    engine_available = any(formula_for(cfg, s["name"]) for s in specs)

    # --- assemble every artifact execution into one batch -------------------
    golden_inputs = [{k: c[k] for k in inputs if k in c} for c in golden_cases]
    batch = list(golden_inputs)

    diff_cases, boundary_count = [], 0
    if engine_available and domains and artifact_output_file is None:
        boundary = generate_boundary_cases(rng, domains)
        boundary_count = len(boundary)
        diff_cases = boundary + [random_case(rng, domains) for _ in range(fuzz_n)]
        diff_start = len(batch)
        batch.extend(diff_cases)

    probes = []
    if artifact_output_file is None:
        probes = build_property_probes(cfg, domains, rng)
        for probe in probes:
            probe["start"] = len(batch)
            batch.extend(probe["cases"])

    # --- execute the artifact ----------------------------------------------
    if artifact_output_file is not None:
        outputs = json.loads(Path(artifact_output_file).read_text(encoding="utf-8"))
        if len(outputs) != len(golden_inputs):
            gaps.append(f"--artifact-output has {len(outputs)} rows but the golden dataset "
                        f"has {len(golden_inputs)} cases")
            return message("blocked", blocked_conf, {"error": "artifact output row mismatch"}, 2)
        gaps.append("artifact executed externally (--artifact-output): differential fuzzing "
                    "and property checks were not run; evidence strength reduced")
    else:
        try:
            outputs = run_artifact(module, batch)
        except Exception as exc:
            gaps.append(f"artifact execution failed: {exc}")
            return message("blocked", blocked_conf, {"error": str(exc)}, 2)

    normalized = [
        {s["name"]: normalize_value(o.get(s["name"]), rounding) for s in specs}
        for o in outputs
    ]

    # --- golden + engine comparison over golden cases -----------------------
    discrepancies, oracle_disagreement = [], []
    matched_units = uncovered_units = 0
    review = load_review(module)

    for i, case in enumerate(golden_cases):
        for s in specs:
            unit_id = f"{i}:{s['name']}"
            artifact_val = normalized[i].get(s["name"])
            golden_val = normalize_value(case.get(s["golden_field"]), rounding)
            fla = formula_for(cfg, s["name"])
            engine_val = None
            if fla is not None:
                engine_val = normalize_value(eval_formula(fla, golden_inputs[i]), rounding)
                if golden_val is not None and not values_match(engine_val, golden_val, s["tolerance"]):
                    oracle_disagreement.append({
                        "unit": unit_id, "inputs": golden_inputs[i],
                        "golden": golden_val, "rule_engine": engine_val,
                        "artifact_agrees_with":
                            "golden" if values_match(artifact_val, golden_val, s["tolerance"])
                            else "rule-engine" if values_match(artifact_val, engine_val, s["tolerance"])
                            else "neither",
                    })

            if golden_val is None:
                uncovered_units += 1  # declared output with no golden value: counts as FN
                continue

            golden_ok = values_match(artifact_val, golden_val, s["tolerance"])
            engine_ok = engine_val is None or values_match(artifact_val, engine_val, s["tolerance"])
            if golden_ok and engine_ok:
                matched_units += 1
            else:
                classification = review["reclassifications"].get(unit_id, "transformation-error")
                discrepancies.append({
                    "unit": unit_id, "inputs": golden_inputs[i],
                    "artifact": artifact_val, "golden": golden_val, "rule_engine": engine_val,
                    "classification": classification,
                    "reviewed": unit_id in review["reclassifications"],
                })

    metrics = compute_metrics(discrepancies, matched_units, uncovered_units,
                              review["escaped_defects"])

    # --- differential fuzz vs the rule engine -------------------------------
    fuzz_result = None
    if diff_cases:
        s0 = specs[0]
        divergences = []
        for j, case in enumerate(diff_cases):
            artifact_val = normalized[diff_start + j].get(s0["name"])
            engine_val = normalize_value(eval_formula(formula_for(cfg, s0["name"]), case), rounding)
            if not values_match(artifact_val, engine_val, s0["tolerance"]):
                divergences.append({"inputs": case, "artifact": artifact_val,
                                    "rule_engine": engine_val})
        fuzz_result = {
            "oracle": "rule-engine",
            "seed": seed,
            "cases_run": len(diff_cases),
            "boundary_cases": boundary_count,
            "random_cases": len(diff_cases) - boundary_count,
            "divergence_count": len(divergences),
            "divergence_rate": round(len(divergences) / len(diff_cases), 4),
            "examples": divergences[:DIVERGENCE_EXAMPLE_LIMIT],
        }
    elif artifact_output_file is None:
        if not engine_available:
            gaps.append("no rule-engine formula for any output field: differential fuzzing "
                        "not possible; single-oracle evidence only")
        if not domains:
            gaps.append("no usable input domains: differential fuzzing not possible")

    # --- property checks -----------------------------------------------------
    property_results = []
    for probe in probes:
        if probe.get("check") is None:
            property_results.append({"type": probe["type"], "over": probe.get("over"),
                                     "status": "not_run", "error": probe.get("error")})
            continue
        outs = normalized[probe["start"]:probe["start"] + len(probe["cases"])]
        violations = probe["check"](outs)
        property_results.append({
            "type": probe["type"],
            "over": probe.get("over"),
            "trials": len(probe["cases"]),
            "violation_count": len(violations),
            "status": "fail" if violations else "pass",
            "examples": violations[:DIVERGENCE_EXAMPLE_LIMIT],
        })

    # --- adequacy + confidence ----------------------------------------------
    adequacy = score_adequacy(cfg, golden, domains, gaps)

    oracles = ["golden-dataset"] + (["rule-engine"] if engine_available else [])
    oracle_factor = 1.0 if len(oracles) == 2 else 0.5
    fuzz_factor = 0.0
    if fuzz_result:
        fuzz_factor = min(1.0, fuzz_result["cases_run"] / FUZZ_FULL_CREDIT_CASES)
    confidence_value = min(CONF_CAP, CONF_ORACLE_WEIGHT * oracle_factor
                           + CONF_ADEQUACY_WEIGHT * adequacy["score"]
                           + CONF_FUZZ_WEIGHT * fuzz_factor)
    band = "high" if confidence_value >= 0.8 else "medium" if confidence_value >= 0.5 else "low"
    basis = (
        f"Calibrated from evidence breadth, not the match rate: oracles={len(oracles)}/2 "
        f"({', '.join(oracles)}), dataset adequacy {adequacy['score']:.2f} "
        f"(volume {adequacy['volume']:.2f}, range {adequacy['range_coverage']:.2f}, "
        f"boundary {adequacy['boundary_coverage']:.2f}, provenance {adequacy['provenance']}), "
        + (f"differential fuzz {fuzz_result['cases_run']} cases (seed {seed})."
           if fuzz_result else "no differential fuzzing run.")
    )

    # --- status --------------------------------------------------------------
    unreviewed = [d for d in discrepancies if d["classification"] == "transformation-error"]
    fuzz_diverged = bool(fuzz_result and fuzz_result["divergence_count"] > 0)
    props_failed = any(p.get("status") == "fail" for p in property_results)
    if unreviewed or fuzz_diverged or props_failed:
        status, exit_code = "fail", 1
    elif oracle_disagreement:
        status, exit_code = "partial", 0
        gaps.append("oracle disagreement found: golden dataset and rule engine differ; "
                    "route to a domain expert, do not resolve silently")
    else:
        status, exit_code = "pass", 0

    result = {
        "unit_of_analysis": "field-per-case",
        "oracles_present": oracles,
        "golden_comparison": {
            "cases": len(golden_cases),
            "units_compared": matched_units + len(discrepancies),
            "matches": matched_units,
        },
        "discrepancies": discrepancies,
        "oracle_disagreement": oracle_disagreement,
        "metrics": metrics,
        "differential_fuzz": fuzz_result,
        "property_checks": property_results,
        "dataset_adequacy": adequacy,
    }
    confidence = {"value": round(confidence_value, 4), "band": band,
                  "source": "calibrated", "basis": basis}
    evidence = [f"rule:{cfg.get('rule_id')}"] if cfg.get("rule_id") else []
    return message(status, confidence, result, exit_code, evidence)


def main():
    parser = argparse.ArgumentParser(description="ParityKit deterministic parity harness")
    parser.add_argument("module", help="module name under input/artifacts/")
    parser.add_argument("--fuzz", type=int, default=500,
                        help="number of random differential-fuzz cases (default 500)")
    parser.add_argument("--seed", type=int, default=1337,
                        help="RNG seed for reproducible fuzz/boundary/property cases")
    parser.add_argument("--artifact-output", default=None,
                        help="precomputed artifact outputs (JSON array aligned with golden "
                             "cases) for environments without node; disables fuzz/properties")
    parser.add_argument("--out", default=None, help="write the skill message JSON here")
    parser.add_argument("--run-id", default=None, help="shared run id for the message chain")
    args = parser.parse_args()

    msg, exit_code = evaluate(args.module, args.fuzz, args.seed,
                              args.artifact_output, args.run_id)
    rendered = json.dumps(msg, indent=2)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")

    m = msg["result"].get("metrics", {})
    fuzz = msg["result"].get("differential_fuzz")
    print(rendered)
    print(
        f"\nparity-evaluation {msg['status'].upper()} — module {msg['module']} — "
        f"match_rate {m.get('match_rate')} — "
        f"precision {m.get('precision')} / recall {m.get('recall')} / f1 {m.get('f1')} — "
        + (f"fuzz {fuzz['divergence_count']}/{fuzz['cases_run']} divergent — " if fuzz else "")
        + f"confidence {msg['confidence']['value']} ({msg['confidence']['band']})",
        file=sys.stderr,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
