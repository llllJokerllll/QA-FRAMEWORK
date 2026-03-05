import { Grid, Box, Typography, ToggleButtonGroup, ToggleButton } from '@mui/material';
import { useState } from 'react';
import AchievementBadge from './AchievementBadge';
import { useAchievementsStore } from '../../stores/achievementsStore';

type FilterType = 'all' | 'unlocked' | 'locked';

export default function AchievementsList() {
  const [filter, setFilter] = useState<FilterType>('all');
  const { achievements } = useAchievementsStore();

  const filteredAchievements = achievements.filter((a) => {
    if (filter === 'unlocked') return a.unlocked;
    if (filter === 'locked') return !a.unlocked;
    return true;
  });

  const handleFilterChange = (_: React.MouseEvent<HTMLElement>, newFilter: FilterType | null) => {
    if (newFilter !== null) {
      setFilter(newFilter);
    }
  };

  const unlockedCount = achievements.filter((a) => a.unlocked).length;
  const totalCount = achievements.length;

  return (
    <Box>
      {/* Header with Stats */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom fontWeight="bold">
            Achievements
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {unlockedCount} of {totalCount} unlocked
          </Typography>
        </Box>

        {/* Filter Toggle */}
        <ToggleButtonGroup
          value={filter}
          exclusive
          onChange={handleFilterChange}
          size="small"
        >
          <ToggleButton value="all">All</ToggleButton>
          <ToggleButton value="unlocked">Unlocked</ToggleButton>
          <ToggleButton value="locked">Locked</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Achievements Grid */}
      <Grid container spacing={3}>
        {filteredAchievements.map((achievement) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={achievement.id}>
            <AchievementBadge achievement={achievement} />
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {filteredAchievements.length === 0 && (
        <Box py={8} textAlign="center">
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No achievements found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {filter === 'unlocked'
              ? "You haven't unlocked any achievements yet. Keep testing!"
              : 'All achievements have been unlocked! 🎉'}
          </Typography>
        </Box>
      )}
    </Box>
  );
}
