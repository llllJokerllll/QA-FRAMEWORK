/**
 * Time calculation utilities for QA-FRAMEWORK
 */

export interface TimeSaved {
  hours: number;
  minutes: number;
  totalMinutes: number;
}

/**
 * Calculate time saved by automation
 * @param numberOfTests Number of tests executed
 * @param automatedTimeMinutes Actual automated execution time in minutes
 * @param manualTestTimeMinutes Average manual test time (default: 15 minutes per test)
 * @returns TimeSaved object with hours, minutes, and totalMinutes
 */
export function calculateTimeSaved(
  numberOfTests: number,
  automatedTimeMinutes: number,
  manualTestTimeMinutes: number = 15
): TimeSaved {
  const manualTimeTotal = numberOfTests * manualTestTimeMinutes;
  const savedMinutes = Math.max(0, manualTimeTotal - automatedTimeMinutes);

  const hours = Math.floor(savedMinutes / 60);
  const minutes = Math.round(savedMinutes % 60);

  return {
    hours,
    minutes,
    totalMinutes: savedMinutes,
  };
}

/**
 * Format time saved as human-readable string
 * @param timeSaved TimeSaved object
 * @returns Formatted string (e.g., "2h 30m")
 */
export function formatTimeSaved(timeSaved: TimeSaved): string {
  if (timeSaved.hours === 0 && timeSaved.minutes === 0) {
    return '0m';
  }

  const parts: string[] = [];
  if (timeSaved.hours > 0) {
    parts.push(`${timeSaved.hours}h`);
  }
  if (timeSaved.minutes > 0) {
    parts.push(`${timeSaved.minutes}m`);
  }

  return parts.join(' ');
}

/**
 * Calculate time saved from execution data
 * @param executions Array of execution objects
 * @returns TimeSaved object with cumulative time saved
 */
export function calculateCumulativeTimeSaved(executions: any[]): TimeSaved {
  let totalManualMinutes = 0;
  let totalAutomatedMinutes = 0;

  executions.forEach((execution) => {
    if (execution.status === 'completed') {
      const testCount = execution.total_tests || 0;
      const durationMinutes = execution.duration ? execution.duration / 60 : 0;

      totalManualMinutes += testCount * 15; // 15 min per test average
      totalAutomatedMinutes += durationMinutes;
    }
  });

  const savedMinutes = Math.max(0, totalManualMinutes - totalAutomatedMinutes);
  const hours = Math.floor(savedMinutes / 60);
  const minutes = Math.round(savedMinutes % 60);

  return {
    hours,
    minutes,
    totalMinutes: savedMinutes,
  };
}

/**
 * Calculate percentage of time saved
 * @param timeSaved TimeSaved object
 * @param totalTests Total number of tests
 * @param manualTestTimeMinutes Manual test time per test
 * @returns Percentage (0-100)
 */
export function calculateTimeSavedPercentage(
  timeSaved: TimeSaved,
  totalTests: number,
  manualTestTimeMinutes: number = 15
): number {
  const totalManualMinutes = totalTests * manualTestTimeMinutes;
  if (totalManualMinutes === 0) return 0;

  const savedPercentage = (timeSaved.totalMinutes / totalManualMinutes) * 100;
  return Math.min(100, Math.round(savedPercentage));
}
