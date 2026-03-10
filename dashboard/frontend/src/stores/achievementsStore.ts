import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Achievement, UserAchievement, AchievementStats } from '../types/achievements';
import { ACHIEVEMENTS } from '../data/achievements';

interface AchievementsState {
  userAchievements: UserAchievement[];
  unlockAchievement: (achievementId: string) => void;
  updateProgress: (achievementId: string, progress: number) => void;
  getStats: () => AchievementStats;
  isUnlocked: (achievementId: string) => boolean;
  getProgress: (achievementId: string) => number;
  reset: () => void;
}

export const useAchievementsStore = create<AchievementsState>()(
  persist(
    (set, get) => ({
      userAchievements: [],

      unlockAchievement: (achievementId: string) => {
        const { userAchievements } = get();

        // Check if already unlocked
        if (userAchievements.some((ua) => ua.achievementId === achievementId)) {
          return;
        }

        const newAchievement: UserAchievement = {
          achievementId,
          unlockedAt: new Date(),
          progress: 100,
        };

        set({
          userAchievements: [...userAchievements, newAchievement],
        });

        // Show notification (you can integrate with toast here)
        const achievement = ACHIEVEMENTS.find((a) => a.id === achievementId);
        if (achievement) {
          console.log(`🎉 Achievement Unlocked: ${achievement.name}!`);
          // TODO: Show toast notification
        }
      },

      updateProgress: (achievementId: string, progress: number) => {
        const { userAchievements } = get();

        const existingIndex = userAchievements.findIndex(
          (ua) => ua.achievementId === achievementId
        );

        if (existingIndex >= 0) {
          // Update existing progress
          const updated = [...userAchievements];
          updated[existingIndex] = {
            ...updated[existingIndex],
            progress: Math.min(100, progress),
          };
          set({ userAchievements: updated });
        } else {
          // Add new progress entry
          set({
            userAchievements: [
              ...userAchievements,
              {
                achievementId,
                unlockedAt: new Date(),
                progress: Math.min(100, progress),
              },
            ],
          });
        }

        // Auto-unlock if progress reaches 100%
        if (progress >= 100) {
          get().unlockAchievement(achievementId);
        }
      },

      getStats: (): AchievementStats => {
        const { userAchievements } = get();

        const unlockedIds = userAchievements
          .filter((ua) => ua.progress >= 100)
          .map((ua) => ua.achievementId);

        const unlockedAchievements = ACHIEVEMENTS.filter((a) =>
          unlockedIds.includes(a.id)
        );

        const totalPoints = unlockedAchievements.reduce(
          (sum, a) => sum + a.points,
          0
        );

        const byCategory = {} as Record<string, number>;
        const byRarity = {} as Record<string, number>;

        unlockedAchievements.forEach((a) => {
          byCategory[a.category] = (byCategory[a.category] || 0) + 1;
          byRarity[a.rarity] = (byRarity[a.rarity] || 0) + 1;
        });

        return {
          totalPoints,
          unlockedCount: unlockedAchievements.length,
          totalCount: ACHIEVEMENTS.length,
          byCategory: byCategory as any,
          byRarity: byRarity as any,
        };
      },

      isUnlocked: (achievementId: string): boolean => {
        const { userAchievements } = get();
        const ua = userAchievements.find((ua) => ua.achievementId === achievementId);
        return ua !== undefined && ua.progress >= 100;
      },

      getProgress: (achievementId: string): number => {
        const { userAchievements } = get();
        const ua = userAchievements.find((ua) => ua.achievementId === achievementId);
        return ua?.progress || 0;
      },

      reset: () => {
        set({ userAchievements: [] });
      },
    }),
    {
      name: 'qa-framework-achievements',
    }
  )
);
