import confetti from 'canvas-confetti';

/**
 * Celebration utilities for test milestones
 * Limits celebrations to 1 per session to avoid spam
 */

const SESSION_KEY_PREFIX = 'qa_framework_celebrated_';

/**
 * Check if a celebration has already happened this session
 */
function hasCelebrated(type: string): boolean {
  return sessionStorage.getItem(SESSION_KEY_PREFIX + type) === 'true';
}

/**
 * Mark a celebration as done for this session
 */
function markCelebrated(type: string): void {
  sessionStorage.setItem(SESSION_KEY_PREFIX + type, 'true');
}

/**
 * Celebrate first successful test
 * Small, subtle confetti burst
 */
export function celebrateFirstSuccess(): void {
  if (hasCelebrated('first_success')) return;

  confetti({
    particleCount: 50,
    spread: 60,
    origin: { y: 0.7 },
    colors: ['#10B981', '#34D399', '#6EE7B7'], // Green tones
  });

  markCelebrated('first_success');
}

/**
 * Celebrate 100% pass rate
 * Big celebration with multiple bursts
 */
export function celebratePerfectRun(): void {
  if (hasCelebrated('perfect_run')) return;

  // First burst - center
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#F59E0B', '#FBBF24', '#FCD34D'], // Gold/yellow tones
  });

  // Second burst - left side
  setTimeout(() => {
    confetti({
      particleCount: 50,
      angle: 60,
      spread: 55,
      origin: { x: 0, y: 0.7 },
      colors: ['#10B981', '#34D399'],
    });
  }, 200);

  // Third burst - right side
  setTimeout(() => {
    confetti({
      particleCount: 50,
      angle: 120,
      spread: 55,
      origin: { x: 1, y: 0.7 },
      colors: ['#3B82F6', '#60A5FA'],
    });
  }, 400);

  markCelebrated('perfect_run');
}

/**
 * Celebrate milestone (10 tests, 50 tests, etc.)
 * Moderate celebration
 */
export function celebrateMilestone(milestone: number): void {
  const key = `milestone_${milestone}`;
  if (hasCelebrated(key)) return;

  confetti({
    particleCount: 80,
    spread: 100,
    origin: { y: 0.5 },
    colors: ['#8B5CF6', '#A78BFA', '#C4B5FD'], // Purple tones
  });

  markCelebrated(key);
}

/**
 * Reset all celebration states (for testing)
 */
export function resetCelebrations(): void {
  Object.keys(sessionStorage)
    .filter(key => key.startsWith(SESSION_KEY_PREFIX))
    .forEach(key => sessionStorage.removeItem(key));
}
