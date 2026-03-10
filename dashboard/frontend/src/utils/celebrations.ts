import confetti from 'canvas-confetti';

// Session storage to prevent spam
let hasCelebratedFirstSuccess = false;
let hasCelebratedPerfectScore = false;

/**
 * Trigger celebration for first successful test
 */
export function celebrateFirstSuccess(): void {
  if (hasCelebratedFirstSuccess) return;
  
  hasCelebratedFirstSuccess = true;
  
  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#10B981', '#34D399', '#6EE7B7'],
  });
}

/**
 * Trigger celebration for 100% pass rate
 */
export function celebratePerfectScore(): void {
  if (hasCelebratedPerfectScore) return;
  
  hasCelebratedPerfectScore = true;
  
  // Multiple bursts for more impact
  const duration = 3 * 1000;
  const animationEnd = Date.now() + duration;
  const colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444'];

  (function frame() {
    confetti({
      particleCount: 4,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors: colors,
    });
    confetti({
      particleCount: 4,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors: colors,
    });

    if (Date.now() < animationEnd) {
      requestAnimationFrame(frame);
    }
  })();
}

/**
 * Trigger celebration for general test success
 */
export function celebrateTestSuccess(): void {
  confetti({
    particleCount: 50,
    spread: 60,
    origin: { y: 0.7 },
    colors: ['#10B981', '#34D399'],
  });
}

/**
 * Reset celebration flags (for new session)
 */
export function resetCelebrations(): void {
  hasCelebratedFirstSuccess = false;
  hasCelebratedPerfectScore = false;
}
