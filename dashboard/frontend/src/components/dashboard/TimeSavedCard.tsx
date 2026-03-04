import { Box, Card, CardContent, Typography, Avatar } from '@mui/material'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import { calculateTimeSaved } from '../../utils/timeCalculations'

interface TimeSavedCardProps {
  executions: number
}

export default function TimeSavedCard({ executions }: TimeSavedCardProps) {
  const timeSaved = calculateTimeSaved(executions)

  return (
    <Card
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 12px 20px -10px rgba(124, 58, 237, 0.5)',
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '120px',
          height: '120%',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1))',
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box>
            <Typography variant="overline" sx={{ opacity: 0.9, letterSpacing: 1 }}>
              Time Saved
            </Typography>
            <Typography variant="h3" fontWeight="bold" sx={{ mt: 1 }}>
              {timeSaved.hours}h {timeSaved.minutes}m
            </Typography>
          </Box>
          <Avatar
            sx={{
              bgcolor: 'rgba(255,255,255,0.2)',
              width: 56,
              height: 56,
            }}
          >
            <AccessTimeIcon sx={{ fontSize: 32 }} />
          </Avatar>
        </Box>
        <Typography
          variant="body2"
          sx={{ mt: 2, opacity: 0.85 }}
        >
          By automating {executions} tests
        </Typography>
      </CardContent>
    </Card>
  )
}
