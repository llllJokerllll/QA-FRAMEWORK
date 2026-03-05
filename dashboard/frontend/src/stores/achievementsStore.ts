import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Achievement } from '../types/achievements';
import { achievements as initialAchievements } from '../data/achievements';

interface AchievementsState {
  achievements: Achievement[];
  totalPoints: number;
  unlockedCount: number;

  // Actions
  unlockAchievement: (id: string) => void;
  updateProgress: (id: string, progress: number) => void;
  resetAchievements: () => void;
  getAchievement: (id: string) => Achievement | undefined;
}

export const useAchievementsStore = create<AchievementsState>()(
  persist(
    (set, get) => ({
      achievements: initialAchievements,
      totalPoints: 0,
      unlockedCount: 0,

      unlockAchievement: (id: string) => {
        set((state) => {
          const achievement = state.achievements.find((a) => a.id === id);
          if (!achievement || achievement.unlocked) return state;

          const updatedAchievements = state.achievements.map((a) =>
            a.id === id
              ? { ...a, unlocked: true, unlockedAt: new Date(), progress: a.total }
              : a
          );

          const newUnlockedCount = updatedAchievements.filter((a) => a.unlocked).length;
          const newTotalPoints = updatedAchievements
            .filter((a) => a.unlocked)
            .reduce((sum, a) => sum + a.points, 0);

          return {
            achievements: updatedAchievements,
            unlockedCount: newUnlockedCount,
            totalPoints: newTotalPoints,
          };
        });
      },

      updateProgress: (id: string, progress: number) => {
        set((state) => {
          const achievement = state.achievements.find((a) => a.id === id);
          if (!achievement || achievement.unlocked) return state;

          const updatedAchievements = state.achievements.map((a) => {
            if (a.id !== id) return a;

            const newProgress = Math.min(progress, a.total || 0);
            const shouldUnlock = newProgress >= (a.total || 0);

            return {
              ...a,
              progress: newProgress,
              unlocked: shouldUnlock,
              unlockedAt: shouldUnlock ? new Date() : undefined,
            };
          });

          const newUnlockedCount = updatedAchievements.filter((a) => a.unlocked).length;
          const newTotalPoints = updatedAchievements
            .filter((a) => a.unlocked)
            .reduce((sum, a) => sum + a.points, 0);

          return {
            achievements: updatedAchievements,
            unlockedCount: newUnlockedCount,
            totalPoints: newTotalPoints,
          };
        });
      },

      resetAchievements: () => {
        set({
          achievements: initialAchievements,
          totalPoints: 0,
          unlockedCount: 0,
        });
      },

      getAchievement: (id: string) => {
        return get().achievements.find((a) => a.id === id);
      },
    }),
    {
      name: 'qa-framework-achievements',
    }
  )
);
