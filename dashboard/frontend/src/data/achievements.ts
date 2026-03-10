import { Achievement } from '../types/achievements';

/**
 * All available achievements in QA-FRAMEWORK
 */
export const ACHIEVEMENTS: Achievement[] = [
  // Testing Achievements
  {
    id: 'first-test',
    name: 'First Steps',
    description: 'Created your first test case',
    icon: '🎯',
    category: 'testing',
    rarity: 'common',
    points: 10,
    requirement: {
      type: 'test_count',
      value: 1,
    },
  },
  {
    id: 'test-suite-master',
    name: 'Test Suite Master',
    description: 'Created 10+ test suites',
    icon: '📦',
    category: 'testing',
    rarity: 'uncommon',
    points: 50,
    requirement: {
      type: 'test_count',
      value: 10,
    },
  },
  {
    id: 'test-expert',
    name: 'Test Expert',
    description: 'Created 100+ test cases',
    icon: '🏆',
    category: 'testing',
    rarity: 'rare',
    points: 100,
    requirement: {
      type: 'test_count',
      value: 100,
    },
  },

  // Automation Achievements
  {
    id: 'automation-pro',
    name: 'Automation Pro',
    description: 'Ran 100+ automated tests',
    icon: '🤖',
    category: 'automation',
    rarity: 'uncommon',
    points: 75,
    requirement: {
      type: 'execution_count',
      value: 100,
    },
  },
  {
    id: 'automation-master',
    name: 'Automation Master',
    description: 'Ran 1000+ automated tests',
    icon: '⚡',
    category: 'automation',
    rarity: 'epic',
    points: 250,
    requirement: {
      type: 'execution_count',
      value: 1000,
    },
  },

  // Quality Achievements
  {
    id: 'bug-hunter',
    name: 'Bug Hunter',
    description: 'Found 10+ bugs with tests',
    icon: '🐛',
    category: 'quality',
    rarity: 'uncommon',
    points: 50,
    requirement: {
      type: 'test_count',
      value: 10,
      metadata: { failed_only: true },
    },
  },
  {
    id: 'perfectionist',
    name: 'Perfectionist',
    description: 'Achieved 100% pass rate in a suite',
    icon: '✨',
    category: 'quality',
    rarity: 'rare',
    points: 100,
    requirement: {
      type: 'pass_rate',
      value: 100,
    },
  },
  {
    id: 'quality-champion',
    name: 'Quality Champion',
    description: 'Maintained 95%+ pass rate for 30 days',
    icon: '👑',
    category: 'quality',
    rarity: 'legendary',
    points: 500,
    requirement: {
      type: 'pass_rate',
      value: 95,
      metadata: { days: 30 },
    },
  },

  // Speed Achievements
  {
    id: 'speed-demon',
    name: 'Speed Demon',
    description: 'Ran a complete test suite in under 1 minute',
    icon: '⚡',
    category: 'speed',
    rarity: 'rare',
    points: 100,
    requirement: {
      type: 'time_based',
      value: 60, // seconds
    },
  },
  {
    id: 'lightning-fast',
    name: 'Lightning Fast',
    description: 'Ran 100 tests in under 5 minutes',
    icon: '🌩️',
    category: 'speed',
    rarity: 'epic',
    points: 200,
    requirement: {
      type: 'time_based',
      value: 300, // seconds
      metadata: { test_count: 100 },
    },
  },

  // Dedication Achievements
  {
    id: 'night-owl',
    name: 'Night Owl',
    description: 'Ran tests after midnight',
    icon: '🦉',
    category: 'dedication',
    rarity: 'common',
    points: 15,
    requirement: {
      type: 'time_based',
      value: 0,
      metadata: { after_hour: 0, before_hour: 6 },
    },
  },
  {
    id: 'early-bird',
    name: 'Early Bird',
    description: 'Ran tests before 6 AM',
    icon: '🐦',
    category: 'dedication',
    rarity: 'common',
    points: 15,
    requirement: {
      type: 'time_based',
      value: 6,
      metadata: { before_hour: 6 },
    },
  },
  {
    id: 'weekend-warrior',
    name: 'Weekend Warrior',
    description: 'Ran tests on a weekend',
    icon: '💪',
    category: 'dedication',
    rarity: 'uncommon',
    points: 25,
    requirement: {
      type: 'time_based',
      value: 0,
      metadata: { weekend_only: true },
    },
  },

  // Special Achievements
  {
    id: 'streak-7',
    name: '7-Day Streak',
    description: 'Ran tests for 7 consecutive days',
    icon: '🔥',
    category: 'special',
    rarity: 'uncommon',
    points: 50,
    requirement: {
      type: 'streak',
      value: 7,
    },
  },
  {
    id: 'streak-30',
    name: '30-Day Streak',
    description: 'Ran tests for 30 consecutive days',
    icon: '🌟',
    category: 'special',
    rarity: 'legendary',
    points: 500,
    requirement: {
      type: 'streak',
      value: 30,
    },
  },
];

/**
 * Get achievement by ID
 */
export function getAchievementById(id: string): Achievement | undefined {
  return ACHIEVEMENTS.find((a) => a.id === id);
}

/**
 * Get achievements by category
 */
export function getAchievementsByCategory(category: string): Achievement[] {
  return ACHIEVEMENTS.filter((a) => a.category === category);
}

/**
 * Get achievements by rarity
 */
export function getAchievementsByRarity(rarity: string): Achievement[] {
  return ACHIEVEMENTS.filter((a) => a.rarity === rarity);
}
