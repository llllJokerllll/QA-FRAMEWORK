import { Card, CardContent, Typography, Box, LinearProgress, Chip } from '@mui/material';
import {
  EmojiEvents as EmojiEventsIcon,
  Star as StarIcon,
  MilitaryTech as MilitaryTechIcon,
  WorkspacePremium as WorkspacePremiumIcon,
  LocalFireDepartment as LocalFireDepartmentIcon,
  AutoFixHigh as AutoFixHighIcon,
  Science as ScienceIcon,
  Bolt as BoltIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import { Achievement, AchievementIcon } from '../../types/achievements';

interface AchievementBadgeProps {
  achievement: Achievement;
}

const iconMap: Record<AchievementIcon, React.ReactElement> = {
  emoji_events: <EmojiEventsIcon />,
  star: <StarIcon />,
  military_tech: <MilitaryTechIcon />,
  workspace_premium: <WorkspacePremiumIcon />,
  local_fire_department: <LocalFireDepartmentIcon />,
  auto_fix_high: <AutoFixHighIcon />,
  science: <ScienceIcon />,
  bolt: <BoltIcon />,
};

const rarityColors: Record<string, string> = {
  common: '#9CA3AF',
  uncommon: '#10B981',
  rare: '#3B82F6',
  epic: '#8B5CF6',
  legendary: '#F59E0B',
};

export default function AchievementBadge({ achievement }: AchievementBadgeProps) {
  const isUnlocked = achievement.unlocked;
  const progress = achievement.progress || 0;
  const total = achievement.total || 1;
  const progressPercentage = (progress / total) * 100;

  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        opacity: isUnlocked ? 1 : 0.7,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: isUnlocked ? 4 : 2,
        },
        border: isUnlocked ? `2px solid ${rarityColors[achievement.rarity]}` : 'none',
      }}
    >
      {/* Locked Overlay */}
      {!isUnlocked && (
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(0, 0, 0, 0.1)',
            zIndex: 1,
          }}
        >
          <LockIcon sx={{ fontSize: 48, color: 'text.disabled' }} />
        </Box>
      )}

      <CardContent>
        {/* Icon and Rarity */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: isUnlocked ? rarityColors[achievement.rarity] : 'grey.300',
              color: 'white',
            }}
          >
            {iconMap[achievement.icon]}
          </Box>
          <Chip
            label={achievement.rarity.toUpperCase()}
            size="small"
            sx={{
              backgroundColor: rarityColors[achievement.rarity],
              color: 'white',
              fontWeight: 'bold',
              fontSize: '0.65rem',
            }}
          />
        </Box>

        {/* Name and Description */}
        <Typography variant="h6" gutterBottom fontWeight="bold">
          {achievement.name}
        </Typography>
        <Typography variant="body2" color="textSecondary" mb={2}>
          {achievement.description}
        </Typography>

        {/* Progress Bar */}
        {achievement.total && achievement.total > 1 && !isUnlocked && (
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" mb={0.5}>
              <Typography variant="caption" color="textSecondary">
                Progress
              </Typography>
              <Typography variant="caption" fontWeight="bold">
                {progress} / {total}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={progressPercentage}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'grey.200',
              }}
            />
          </Box>
        )}

        {/* Points */}
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="body2" color="textSecondary">
            Points
          </Typography>
          <Typography variant="h6" fontWeight="bold" color="primary">
            {achievement.points}
          </Typography>
        </Box>

        {/* Unlocked Date */}
        {isUnlocked && achievement.unlockedAt && (
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
            Unlocked: {new Date(achievement.unlockedAt).toLocaleDateString()}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
