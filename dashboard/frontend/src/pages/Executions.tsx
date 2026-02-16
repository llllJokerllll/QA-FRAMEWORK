import { useQuery } from 'react-query'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  CircularProgress,
} from '@mui/material'
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material'
import { executionsAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function Executions() {
  const { data: executions, isLoading, refetch } = useQuery('executions', () =>
    executionsAPI.getAll()
  )

  const startExecution = (executionId: number) => {
    executionsAPI.start(executionId).then(() => {
      toast.success('Execution started')
      refetch()
    }).catch(() => {
      toast.error('Failed to start execution')
    })
  }

  const stopExecution = (executionId: number) => {
    executionsAPI.stop(executionId).then(() => {
      toast.success('Execution stopped')
      refetch()
    }).catch(() => {
      toast.error('Failed to stop execution')
    })
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Test Executions</Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Suite</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Environment</TableCell>
              <TableCell>Started</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Results</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions?.data?.map((execution: any) => (
              <TableRow key={execution.id}>
                <TableCell>{execution.id}</TableCell>
                <TableCell>{execution.suite_name}</TableCell>
                <TableCell>
                  <Chip
                    label={execution.status}
                    color={
                      execution.status === 'completed'
                        ? 'success'
                        : execution.status === 'running'
                        ? 'primary'
                        : execution.status === 'failed'
                        ? 'error'
                        : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip label={execution.environment} size="small" />
                </TableCell>
                <TableCell>{new Date(execution.started_at).toLocaleString()}</TableCell>
                <TableCell>{execution.duration ? `${execution.duration}s` : '-'}</TableCell>
                <TableCell>
                  <Box display="flex" gap={0.5}>
                    <Chip
                      label={`P:${execution.passed_tests}`}
                      size="small"
                      color="success"
                    />
                    <Chip
                      label={`F:${execution.failed_tests}`}
                      size="small"
                      color="error"
                    />
                    <Chip
                      label={`S:${execution.skipped_tests}`}
                      size="small"
                      color="warning"
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  {execution.status === 'running' ? (
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => stopExecution(execution.id)}
                    >
                      <StopIcon />
                    </IconButton>
                  ) : (
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => startExecution(execution.id)}
                    >
                      <PlayArrowIcon />
                    </IconButton>
                  )}
                  <IconButton size="small">
                    <VisibilityIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}