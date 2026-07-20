// Generic ParityKit artifact runner.
//
// Usage: node scripts/run_artifact.mjs <path/to/module/harness.mjs>
//
// Reads a JSON array of case-input objects on stdin, executes the module's
// harness once per case, and writes the JSON array of output objects to
// stdout. Every module under input/artifacts/{module}/ that wants automated
// parity evaluation provides a harness.mjs exporting:
//
//     export function runCase(input) -> output object
//
// The harness owns the mapping between ParityKit's named case inputs and the
// artifact's actual call signature; this runner stays artifact-agnostic.
// TypeScript artifacts can be imported directly (Node >= 23 strips types).
import { pathToFileURL } from "node:url";

const harnessPath = process.argv[2];
if (!harnessPath) {
  console.error("usage: node scripts/run_artifact.mjs <path/to/harness.mjs>");
  process.exit(2);
}

const harness = await import(pathToFileURL(harnessPath).href);
if (typeof harness.runCase !== "function") {
  console.error(`${harnessPath} must export runCase(input) -> output object`);
  process.exit(2);
}

let raw = "";
for await (const chunk of process.stdin) raw += chunk;
const cases = JSON.parse(raw);

const outputs = [];
for (const c of cases) outputs.push(await harness.runCase(c));
process.stdout.write(JSON.stringify(outputs));
