import { Card, CardContent, Typography, Box } from '@mui/material';
import { Schedule as ScheduleIcon } from '@mui/icons-material';
import { calculateTimeSaved, TimeSavedResult } from '../../utils/timeCalculations';

interface TimeSavedCardProps {
  executions: number;
  testCount?: number; // Optional: if not provided, uses executions
  automatedTimeMinutes?: number; // Optional: defaults to 2 min per execution
}

export default function TimeSavedCard({
  executions,
  testCount,
  automatedTimeMinutes
}: TimeSavedCardProps) {
  // Use testCount if provided, otherwise estimate from executions
  const actualTestCount = testCount || executions * 5; // Assume 5 tests per execution

  // Use automatedTimeMinutes if provided, otherwise estimate
  const actualAutomatedTime = automatedTimeMinutes || executions * 2; // Assume 2 min per execution

  const timeSaved: TimeSavedResult = calculateTimeSaved(actualTestCount, actualAutomatedTime);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <ScheduleIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
          <Typography variant="h6" component="div">
            Time Saved
          </Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="h3" component="div" color="primary" fontWeight="bold">
            {timeSaved.formatted}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            by automating {actualTestCount} tests
          </Typography>
        </Box>

        <Box
          sx={{
            backgroundColor: 'success.light',
            borderRadius: 1,
            p: 1.5,
            mt: 2,
          }}
        >
          <Typography variant="body2" color="success.contrastText">
            <strong>Calculation:</strong>
          </Typography>
          <Typography variant="body2" color="success.contrastText">
            • Manual: {actualTestCount} × 15min = {(actualTestCount * 15).toFixed(0)}min
          </Typography>
          <Typography variant="body2" color="success.contrastText">
            • Automated: {actualAutomatedTime}min
          </Typography>
          <Typography variant="body2" color="success.contrastText" fontWeight="bold">
            • Saved: {timeSaved.totalMinutes}min
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
