import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { suitesAPI, executionsAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function TestSuites() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [openDialog, setOpenDialog] = useState(false)
  const [editingSuite, setEditingSuite] = useState<any>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    framework_type: 'pytest',
  })

  const { data: suites, isLoading } = useQuery('suites', () => suitesAPI.getAll())

  const createMutation = useMutation(
    (data: any) => suitesAPI.create(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('suites')
        toast.success('Suite created successfully')
        handleCloseDialog()
      },
      onError: () => toast.error('Failed to create suite'),
    }
  )

  const deleteMutation = useMutation(
    (id: number) => suitesAPI.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('suites')
        toast.success('Suite deleted successfully')
      },
      onError: () => toast.error('Failed to delete suite'),
    }
  )

  const executeMutation = useMutation(
    (suiteId: number) => executionsAPI.create({ suite_id: suiteId }),
    {
      onSuccess: (response) => {
        toast.success('Execution started')
        navigate('/executions')
      },
      onError: () => toast.error('Failed to start execution'),
    }
  )

  const handleOpenDialog = (suite?: any) => {
    if (suite) {
      setEditingSuite(suite)
      setFormData({
        name: suite.name,
        description: suite.description || '',
        framework_type: suite.framework_type,
      })
    } else {
      setEditingSuite(null)
      setFormData({ name: '', description: '', framework_type: 'pytest' })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingSuite(null)
  }

  const handleSubmit = () => {
    if (!formData.name) {
      toast.error('Name is required')
      return
    }
    createMutation.mutate(formData)
  }

  if (isLoading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Test Suites</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Suite
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Framework</TableCell>
              <TableCell>Test Cases</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {suites?.data?.map((suite: any) => (
              <TableRow key={suite.id}>
                <TableCell>{suite.name}</TableCell>
                <TableCell>{suite.description}</TableCell>
                <TableCell>
                  <Chip label={suite.framework_type} size="small" />
                </TableCell>
                <TableCell>{suite.tests?.length || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={suite.is_active ? 'Active' : 'Inactive'}
                    color={suite.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => navigate(`/suites/${suite.id}/cases`)}
                  >
                    <AddIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => executeMutation.mutate(suite.id)}
                  >
                    <PlayArrowIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(suite)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => deleteMutation.mutate(suite.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSuite ? 'Edit Test Suite' : 'Create Test Suite'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            select
            label="Framework Type"
            value={formData.framework_type}
            onChange={(e) => setFormData({ ...formData, framework_type: e.target.value })}
            margin="normal"
            SelectProps={{
              native: true,
            }}
          >
            <option value="pytest">Pytest</option>
            <option value="unittest">Unittest</option>
            <option value="robot">Robot Framework</option>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingSuite ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}