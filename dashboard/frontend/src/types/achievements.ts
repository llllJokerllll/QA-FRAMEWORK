/**
 * Achievement types for QA-FRAMEWORK gamification system
 */

export type AchievementCategory =
  | 'tests'
  | 'execution'
  | 'streak'
  | 'feature'
  | 'special';

export type AchievementIcon =
  | 'emoji_events'
  | 'star'
  | 'military_tech'
  | 'workspace_premium'
  | 'local_fire_department'
  | 'auto_fix_high'
  | 'science'
  | 'bolt';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: AchievementIcon;
  category: AchievementCategory;
  unlocked: boolean;
  unlockedAt?: Date;
  progress?: number; // Current progress (e.g., 7 for "7-Day Streak")
  total?: number; // Total needed (e.g., 7 for "7-Day Streak")
  points: number; // Gamification points
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
}

export interface UserAchievements {
  userId: string;
  totalPoints: number;
  achievements: Achievement[];
  unlockedCount: number;
  totalCount: number;
}
