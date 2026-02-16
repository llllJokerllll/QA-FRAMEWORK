import { useQuery } from 'react-query'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
} from '@mui/material'
import {
  TrendingUp,
  TrendingDown,
  Folder,
  PlayArrow,
  CheckCircle,
  Error,
} from '@mui/icons-material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import { dashboardAPI } from '../api/client'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery('dashboard-stats', () =>
    dashboardAPI.getStats()
  )

  const { data: trends, isLoading: trendsLoading } = useQuery('dashboard-trends', () =>
    dashboardAPI.getTrends(30)
  )

  const { data: recent, isLoading: recentLoading } = useQuery('dashboard-recent', () =>
    dashboardAPI.getRecentExecutions(10)
  )

  if (statsLoading || trendsLoading || recentLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    )
  }

  const statsData = stats?.data
  const trendsData = trends?.data || []
  const recentData = recent?.data || []

  // Chart data
  const lineChartData = {
    labels: trendsData.map((t: any) => t.date),
    datasets: [
      {
        label: 'Total Executions',
        data: trendsData.map((t: any) => t.total),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
        label: 'Passed',
        data: trendsData.map((t: any) => t.passed),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
      },
      {
        label: 'Failed',
        data: trendsData.map((t: any) => t.failed),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
      },
    ],
  }

  const testTypeData = {
    labels: ['API', 'UI', 'DB', 'Security', 'Performance'],
    datasets: [
      {
        data: [12, 19, 3, 5, 2],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 92, 246, 0.8)',
        ],
      },
    ],
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Executions
                  </Typography>
                  <Typography variant="h4">
                    {statsData?.total_executions || 0}
                  </Typography>
                </Box>
                <PlayArrow color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Test Suites
                  </Typography>
                  <Typography variant="h4">
                    {statsData?.total_test_suites || 0}
                  </Typography>
                </Box>
                <Folder color="secondary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Success Rate
                  </Typography>
                  <Typography variant="h4">
                    {statsData?.success_rate || 0}%
                  </Typography>
                </Box>
                {statsData?.success_rate >= 80 ? (
                  <TrendingUp color="success" sx={{ fontSize: 40 }} />
                ) : (
                  <TrendingDown color="error" sx={{ fontSize: 40 }} />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Duration
                  </Typography>
                  <Typography variant="h4">
                    {statsData?.average_duration || 0}s
                  </Typography>
                </Box>
                <CheckCircle color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Execution Trends (Last 30 Days)
              </Typography>
              <Line data={lineChartData} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Types Distribution
              </Typography>
              <Doughnut data={testTypeData} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Executions */}
      <Box sx={{ mt: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Executions
            </Typography>
            {recentData.map((execution: any) => (
              <Box
                key={execution.id}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                sx={{ py: 1, borderBottom: '1px solid #333' }}
              >
                <Box>
                  <Typography variant="body1">{execution.suite_name}</Typography>
                  <Typography variant="caption" color="textSecondary">
                    {execution.environment} • {execution.started_at}
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip
                    size="small"
                    label={`${execution.passed}/${execution.total_tests} passed`}
                    color={execution.passed === execution.total_tests ? 'success' : 'warning'}
                  />
                  <Chip
                    size="small"
                    label={execution.status}
                    color={
                      execution.status === 'completed'
                        ? 'success'
                        : execution.status === 'running'
                        ? 'primary'
                        : 'error'
                    }
                  />
                </Box>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}