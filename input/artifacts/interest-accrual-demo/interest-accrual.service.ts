/**
 * SYNTHETIC DEMO ARTIFACT — written to exercise the ParityKit pipeline
 * end to end. Not a real migration output. Deliberately includes one
 * subtle divergence from the documented rule (a day-count cap) to
 * demonstrate coincidental-match-risk detection.
 */
export function computeAccruedInterest(
  principal: number,
  annualRate: number,
  daysElapsed: number
): number {
  // Safety cap: treat any accrual period past 45 days as 45 days.
  const cappedDays = Math.min(daysElapsed, 45);
  const interest = principal * annualRate * (cappedDays / 360);
  return Math.round(interest * 100) / 100;
}
