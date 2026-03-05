import { Achievement } from '../types/achievements';

/**
 * All available achievements in QA-FRAMEWORK
 */
export const achievements: Achievement[] = [
  // Test Creation Achievements
  {
    id: 'first_test',
    name: 'First Steps',
    description: 'Create your first test case',
    icon: 'emoji_events',
    category: 'tests',
    unlocked: false,
    progress: 0,
    total: 1,
    points: 10,
    rarity: 'common',
  },
  {
    id: 'ten_tests',
    name: 'Getting Started',
    description: 'Create 10 test cases',
    icon: 'star',
    category: 'tests',
    unlocked: false,
    progress: 0,
    total: 10,
    points: 25,
    rarity: 'uncommon',
  },
  {
    id: 'fifty_tests',
    name: 'Test Master',
    description: 'Create 50 test cases',
    icon: 'military_tech',
    category: 'tests',
    unlocked: false,
    progress: 0,
    total: 50,
    points: 100,
    rarity: 'rare',
  },

  // Execution Achievements
  {
    id: 'first_success',
    name: 'Green Light',
    description: 'Complete your first successful test run',
    icon: 'workspace_premium',
    category: 'execution',
    unlocked: false,
    progress: 0,
    total: 1,
    points: 15,
    rarity: 'common',
  },
  {
    id: 'perfect_run',
    name: 'Perfectionist',
    description: 'Achieve 100% pass rate on a test run with 10+ tests',
    icon: 'emoji_events',
    category: 'execution',
    unlocked: false,
    progress: 0,
    total: 1,
    points: 50,
    rarity: 'epic',
  },

  // Streak Achievements
  {
    id: 'seven_day_streak',
    name: 'On Fire!',
    description: 'Use QA-FRAMEWORK for 7 consecutive days',
    icon: 'local_fire_department',
    category: 'streak',
    unlocked: false,
    progress: 0,
    total: 7,
    points: 75,
    rarity: 'rare',
  },

  // Feature Achievements
  {
    id: 'self_healing_used',
    name: 'Self-Healing Pioneer',
    description: 'Use the AI self-healing feature',
    icon: 'auto_fix_high',
    category: 'feature',
    unlocked: false,
    progress: 0,
    total: 1,
    points: 30,
    rarity: 'uncommon',
  },

  // Special Achievements
  {
    id: 'beta_tester',
    name: 'Beta Tester',
    description: 'Joined during the beta period',
    icon: 'science',
    category: 'special',
    unlocked: false,
    progress: 0,
    total: 1,
    points: 200,
    rarity: 'legendary',
  },
];

/**
 * Get achievements by category
 */
export function getAchievementsByCategory(category: string): Achievement[] {
  return achievements.filter((a) => a.category === category);
}

/**
 * Get unlocked achievements
 */
export function getUnlockedAchievements(): Achievement[] {
  return achievements.filter((a) => a.unlocked);
}

/**
 * Get locked achievements
 */
export function getLockedAchievements(): Achievement[] {
  return achievements.filter((a) => !a.unlocked);
}

/**
 * Calculate total points from unlocked achievements
 */
export function calculateTotalPoints(unlockedIds: string[]): number {
  return achievements
    .filter((a) => unlockedIds.includes(a.id))
    .reduce((sum, a) => sum + a.points, 0);
}
