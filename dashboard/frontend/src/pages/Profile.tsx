import { Box, Typography, Card, CardContent, Avatar, Grid, Chip } from '@mui/material';
import { Person as PersonIcon, EmojiEvents as EmojiEventsIcon } from '@mui/icons-material';
import AchievementsList from '../components/achievements/AchievementsList';
import { useAchievementsStore } from '../stores/achievementsStore';

export default function Profile() {
  const { totalPoints, unlockedCount, achievements } = useAchievementsStore();

  // Mock user data (in production, this would come from auth/API)
  const user = {
    name: 'Joker',
    email: 'joker@qaframework.io',
    avatar: null,
    joinDate: new Date('2026-02-01'),
  };

  // Calculate stats
  const totalCount = achievements.length;
  const completionPercentage = Math.round((unlockedCount / totalCount) * 100);

  return (
    <Box>
      {/* Header */}
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Profile
      </Typography>

      {/* User Info Card */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            {/* Avatar */}
            <Grid item>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  bgcolor: 'primary.main',
                  fontSize: '2rem',
                }}
              >
                {user.avatar ? (
                  <img src={user.avatar} alt={user.name} />
                ) : (
                  <PersonIcon sx={{ fontSize: 40 }} />
                )}
              </Avatar>
            </Grid>

            {/* User Details */}
            <Grid item xs>
              <Typography variant="h5" fontWeight="bold">
                {user.name}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {user.email}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Member since {user.joinDate.toLocaleDateString()}
              </Typography>
            </Grid>

            {/* Stats */}
            <Grid item>
              <Box textAlign="right">
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <EmojiEventsIcon color="primary" />
                  <Typography variant="h4" fontWeight="bold" color="primary">
                    {totalPoints}
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Total Points
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h3" fontWeight="bold" color="primary">
                {unlockedCount}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Achievements Unlocked
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h3" fontWeight="bold" color="secondary">
                {totalCount - unlockedCount}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Achievements Locked
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Typography variant="h3" fontWeight="bold">
                {completionPercentage}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Completion Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Achievements List */}
      <AchievementsList />
    </Box>
  );
}
