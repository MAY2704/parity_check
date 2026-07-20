#!/usr/bin/env python3
"""Unit tests for scripts/parity_eval.py. Dependency-free (stdlib unittest);
run from the repo root:

    python scripts/test_parity_eval.py
"""
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import parity_eval as pe


class TestFormulaEvaluator(unittest.TestCase):
    def test_arithmetic(self):
        self.assertAlmostEqual(
            pe.eval_formula("principal * annual_rate * (days_elapsed / 360)",
                            {"principal": 10000, "annual_rate": 0.05, "days_elapsed": 30}),
            41.666666, places=4)

    def test_functions(self):
        self.assertEqual(pe.eval_formula("min(a, 45) + max(b, 0) + abs(-2)", {"a": 50, "b": -1}), 47.0)

    def test_undeclared_input_rejected(self):
        with self.assertRaises(ValueError):
            pe.eval_formula("a + b", {"a": 1})

    def test_disallowed_construct_rejected(self):
        with self.assertRaises(ValueError):
            pe.eval_formula("__import__('os').getcwd()", {})


class TestNormalization(unittest.TestCase):
    ROUNDING = {"mode": "half_up", "decimal_places": 2}

    def test_half_up(self):
        self.assertEqual(pe.normalize_value(41.66666, self.ROUNDING), 41.67)
        self.assertEqual(pe.normalize_value(2.675, self.ROUNDING), 2.68)  # not banker's

    def test_half_even(self):
        self.assertEqual(pe.normalize_value(2.675, {"mode": "half_even", "decimal_places": 2}), 2.68)
        self.assertEqual(pe.normalize_value(2.665, {"mode": "half_even", "decimal_places": 2}), 2.66)

    def test_no_rounding_declared(self):
        self.assertEqual(pe.normalize_value(2.6751, {}), 2.6751)

    def test_non_numeric_passthrough(self):
        self.assertIsNone(pe.normalize_value(None, self.ROUNDING))
        self.assertEqual(pe.normalize_value("N/A", self.ROUNDING), "N/A")

    def test_default_tolerance(self):
        self.assertEqual(pe.default_tolerance(self.ROUNDING), 0.005)
        self.assertEqual(pe.default_tolerance({}), 0.0)

    def test_values_match(self):
        self.assertTrue(pe.values_match(41.67, 41.665, 0.005))
        self.assertFalse(pe.values_match(41.67, 41.66, 0.005))
        self.assertFalse(pe.values_match(None, 41.67, 0.005))


class TestMetrics(unittest.TestCase):
    def test_reference_worked_example(self):
        """The worked example in parity-evaluation/REFERENCE.md: TP=2 FP=1 FN=2 TN=35."""
        discrepancies = [
            {"classification": "transformation-error"},
            {"classification": "transformation-error"},
            {"classification": "tolerance-acceptable"},
        ]
        m = pe.compute_metrics(discrepancies, matched_units=35, uncovered_units=2,
                               escaped_defects=[])
        self.assertEqual((m["tp"], m["fp"], m["fn"], m["tn"]), (2, 1, 2, 35))
        self.assertAlmostEqual(m["precision"], 0.6667, places=4)
        self.assertAlmostEqual(m["recall"], 0.5, places=4)
        self.assertAlmostEqual(m["accuracy"], 0.925, places=4)
        self.assertAlmostEqual(m["f1"], 0.5714, places=4)

    def test_degenerate_clean_run_reports_null_not_one(self):
        """A clean run (nothing flagged, nothing missed) must report null
        metrics, never a fabricated 1.0 — the v2.0.0 demo-report bug."""
        m = pe.compute_metrics([], matched_units=5, uncovered_units=0, escaped_defects=[])
        self.assertIsNone(m["precision"])
        self.assertIsNone(m["recall"])
        self.assertIsNone(m["f1"])
        self.assertEqual(m["accuracy"], 1.0)
        self.assertEqual(m["match_rate"], 1.0)
        self.assertEqual(m["oracle_coverage"], 1.0)
        self.assertTrue(m["degenerate_notes"])

    def test_uncovered_units_are_hard_fn(self):
        m = pe.compute_metrics([], matched_units=5, uncovered_units=3, escaped_defects=[])
        self.assertEqual(m["fn"], 3)
        self.assertEqual(m["recall"], 0.0)          # defined: TP=0, FN=3
        self.assertIsNone(m["precision"])           # still nothing flagged
        self.assertAlmostEqual(m["oracle_coverage"], 0.625)

    def test_flagged_is_provisional_tp_until_reviewed(self):
        flagged = [{"classification": "transformation-error"}]
        m = pe.compute_metrics(flagged, matched_units=4, uncovered_units=0, escaped_defects=[])
        self.assertEqual(m["tp"], 1)
        self.assertEqual(m["precision"], 1.0)
        reclassified = [{"classification": "legacy-defect-now-fixed"}]
        m2 = pe.compute_metrics(reclassified, matched_units=4, uncovered_units=0,
                                escaped_defects=[])
        self.assertEqual((m2["tp"], m2["fp"]), (0, 1))
        self.assertEqual(m2["precision"], 0.0)

    def test_escaped_defects_count_as_fn(self):
        m = pe.compute_metrics([], matched_units=10, uncovered_units=0,
                               escaped_defects=[{"unit": "3:fee", "note": "found in UAT"}])
        self.assertEqual(m["fn"], 1)
        self.assertEqual(m["recall"], 0.0)


class TestCaseGeneration(unittest.TestCase):
    DOMAINS = {
        "principal": {"min": 0, "max": 1000},
        "days": {"min": 0, "max": 360, "integer": True, "boundary_values": [30, 31]},
    }

    def test_boundary_values_include_edges_and_declared(self):
        vals = pe.boundary_values_for(self.DOMAINS["days"])
        for expected in (0, 30, 31, 180, 360):
            self.assertIn(expected, vals)

    def test_boundary_cases_pin_each_value(self):
        rng = random.Random(1)
        cases = pe.generate_boundary_cases(rng, self.DOMAINS, fills_per_value=2)
        self.assertTrue(any(c["days"] == 31 for c in cases))
        self.assertTrue(all(0 <= c["principal"] <= 1000 for c in cases))
        # deduplicated
        keys = [tuple(sorted(c.items())) for c in cases]
        self.assertEqual(len(keys), len(set(keys)))

    def test_fuzz_respects_integer_domains(self):
        rng = random.Random(2)
        for _ in range(50):
            case = pe.random_case(rng, self.DOMAINS)
            self.assertIsInstance(case["days"], int)
            self.assertTrue(0 <= case["days"] <= 360)


class TestAdequacy(unittest.TestCase):
    def _cfg(self):
        return {"adequacy": {"target_case_count": 50}}

    def test_small_synthetic_dataset_scores_low(self):
        golden = {"provenance": "synthetic",
                  "cases": [{"x": 10, "y": 1}, {"x": 20, "y": 2}]}
        domains = {"x": {"min": 0, "max": 100}, "y": {"min": 0, "max": 10}}
        gaps = []
        a = pe.score_adequacy(self._cfg(), golden, domains, gaps)
        self.assertEqual(a["case_count"], 2)
        self.assertAlmostEqual(a["volume"], 0.04)
        self.assertLess(a["score"], 0.3)
        self.assertEqual(gaps, [])

    def test_missing_provenance_is_a_gap(self):
        golden = {"cases": [{"x": 5, "y": 5}]}
        gaps = []
        a = pe.score_adequacy(self._cfg(), golden, {"x": {"min": 0, "max": 10}}, gaps)
        self.assertEqual(a["provenance"], "undeclared")
        self.assertEqual(a["provenance_factor"], 0.0)
        self.assertTrue(gaps)

    def test_full_range_and_boundaries_score_high(self):
        domains = {"x": {"min": 0, "max": 100, "boundary_values": [50]}}
        golden = {"provenance": "production",
                  "cases": [{"x": v} for v in (0, 25, 50, 75, 100)] * 10}
        a = pe.score_adequacy(self._cfg(), golden, domains, [])
        self.assertEqual(a["volume"], 1.0)
        self.assertEqual(a["range_coverage"], 1.0)
        self.assertEqual(a["boundary_coverage"], 1.0)
        self.assertGreater(a["score"], 0.95)


class TestEvaluateIntegration(unittest.TestCase):
    """Runs evaluate() against the real demo module with a precomputed clean
    artifact output (no node needed), and checks the message against the
    skill-message schema."""

    def _clean_outputs(self):
        golden = json.loads((pe.ROOT / "context" / "golden-datasets" /
                             "interest-accrual-demo" / "golden.json").read_text(encoding="utf-8"))
        outs = []
        for c in golden["cases"]:
            v = c["principal"] * c["annual_rate"] * (c["days_elapsed"] / 360)
            outs.append({"accrued_interest": round(v, 2)})
        return outs

    def test_clean_artifact_passes_with_degenerate_metrics_and_valid_message(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(self._clean_outputs(), f)
            path = f.name
        try:
            msg, exit_code = pe.evaluate("interest-accrual-demo", fuzz_n=0, seed=1,
                                         artifact_output_file=path, run_id="run-test")
        finally:
            Path(path).unlink()

        self.assertEqual(exit_code, 0)
        self.assertEqual(msg["status"], "pass")
        m = msg["result"]["metrics"]
        self.assertIsNone(m["precision"])
        self.assertIsNone(m["f1"])
        self.assertEqual(m["match_rate"], 1.0)
        # external execution => no fuzz/properties => reduced evidence, flagged as a gap
        self.assertIsNone(msg["result"]["differential_fuzz"])
        self.assertTrue(any("artifact executed externally" in g for g in msg["gaps"]))
        self.assertLess(msg["confidence"]["value"], 0.75)

        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema = json.loads((pe.ROOT / "context" / "schemas" /
                             "skill-message.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(instance=msg, schema=schema)

    def test_divergent_artifact_output_fails(self):
        outs = self._clean_outputs()
        outs[2]["accrued_interest"] += 5.0
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(outs, f)
            path = f.name
        try:
            msg, exit_code = pe.evaluate("interest-accrual-demo", fuzz_n=0, seed=1,
                                         artifact_output_file=path, run_id="run-test")
        finally:
            Path(path).unlink()
        self.assertEqual(exit_code, 1)
        self.assertEqual(msg["status"], "fail")
        self.assertEqual(len(msg["result"]["discrepancies"]), 1)
        self.assertEqual(msg["result"]["metrics"]["precision"], 1.0)  # 1 flagged, provisional TP


if __name__ == "__main__":
    unittest.main(verbosity=2)
