/**
 * Time calculation utilities for QA-FRAMEWORK
 * Calculate time saved by test automation
 */

/**
 * Average time for manual test execution (in minutes)
 * Industry standard: 15-30 minutes per test case
 */
const MANUAL_TEST_TIME_MINUTES = 15;

/**
 * Result of time saved calculation
 */
export interface TimeSavedResult {
  hours: number;
  minutes: number;
  totalMinutes: number;
  formatted: string;
}

/**
 * Calculate time saved by automation
 *
 * @param testCount - Number of tests automated
 * @param automatedTimeMinutes - Time taken to run automated tests (in minutes)
 * @returns TimeSavedResult with hours, minutes, and formatted string
 *
 * @example
 * calculateTimeSaved(50, 30)
 * // Returns: { hours: 12, minutes: 30, totalMinutes: 750, formatted: "12h 30m" }
 * // (50 tests * 15 min) - 30 min = 750 - 30 = 720 minutes = 12h
 */
export function calculateTimeSaved(
  testCount: number,
  automatedTimeMinutes: number
): TimeSavedResult {
  const manualTimeMinutes = testCount * MANUAL_TEST_TIME_MINUTES;
  const savedMinutes = Math.max(0, manualTimeMinutes - automatedTimeMinutes);

  const hours = Math.floor(savedMinutes / 60);
  const minutes = Math.round(savedMinutes % 60);

  return {
    hours,
    minutes,
    totalMinutes: savedMinutes,
    formatted: `${hours}h ${minutes}m`,
  };
}

/**
 * Calculate time saved percentage
 *
 * @param testCount - Number of tests automated
 * @param automatedTimeMinutes - Time taken to run automated tests (in minutes)
 * @returns Percentage of time saved (0-100)
 *
 * @example
 * calculateTimeSavedPercentage(50, 30)
 * // Returns: 96
 * // (750 - 30) / 750 * 100 = 96%
 */
export function calculateTimeSavedPercentage(
  testCount: number,
  automatedTimeMinutes: number
): number {
  const manualTimeMinutes = testCount * MANUAL_TEST_TIME_MINUTES;
  if (manualTimeMinutes === 0) return 0;

  const savedMinutes = manualTimeMinutes - automatedTimeMinutes;
  const percentage = (savedMinutes / manualTimeMinutes) * 100;

  return Math.min(100, Math.max(0, Math.round(percentage)));
}

/**
 * Format minutes into human-readable string
 *
 * @param totalMinutes - Total minutes to format
 * @returns Formatted string (e.g., "2h 30m" or "45m")
 */
export function formatTime(totalMinutes: number): string {
  if (totalMinutes < 60) {
    return `${Math.round(totalMinutes)}m`;
  }

  const hours = Math.floor(totalMinutes / 60);
  const minutes = Math.round(totalMinutes % 60);

  if (minutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${minutes}m`;
}

/**
 * Estimate manual test time for a given number of tests
 *
 * @param testCount - Number of tests
 * @returns Estimated time in minutes
 */
export function estimateManualTestTime(testCount: number): number {
  return testCount * MANUAL_TEST_TIME_MINUTES;
}
