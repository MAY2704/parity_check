// ParityKit execution harness for the interest-accrual-demo artifact.
// Maps ParityKit's named case inputs (from the rule config / golden dataset)
// onto the artifact's actual call signature. Run via scripts/run_artifact.mjs.
import { computeAccruedInterest } from "./interest-accrual.service.ts";

export function runCase({ principal, annual_rate, days_elapsed }) {
  return { accrued_interest: computeAccruedInterest(principal, annual_rate, days_elapsed) };
}
