/**
 * Achievement types for QA-FRAMEWORK gamification system
 */

export type AchievementCategory =
  | 'testing'
  | 'automation'
  | 'quality'
  | 'speed'
  | 'dedication'
  | 'special';

export type AchievementRarity = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string; // Emoji or icon identifier
  category: AchievementCategory;
  rarity: AchievementRarity;
  points: number;
  requirement: {
    type: 'test_count' | 'execution_count' | 'pass_rate' | 'time_based' | 'streak';
    value: number;
    metadata?: Record<string, any>;
  };
  unlockedAt?: Date;
  progress?: number; // 0-100
}

export interface UserAchievement {
  achievementId: string;
  unlockedAt: Date;
  progress: number;
}

export interface AchievementStats {
  totalPoints: number;
  unlockedCount: number;
  totalCount: number;
  byCategory: Record<AchievementCategory, number>;
  byRarity: Record<AchievementRarity, number>;
}
