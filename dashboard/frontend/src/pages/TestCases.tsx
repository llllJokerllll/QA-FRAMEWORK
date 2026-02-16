import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useParams, useNavigate } from 'react-router-dom'
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material'
import { casesAPI } from '../api/client'
import toast from 'react-hot-toast'

export default function TestCases() {
  const { suiteId } = useParams<{ suiteId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [openDialog, setOpenDialog] = useState(false)
  const [editingCase, setEditingCase] = useState<any>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_code: '',
    test_type: 'api',
    priority: 'medium',
    tags: '',
  })

  const { data: cases, isLoading } = useQuery(['cases', suiteId], () =>
    casesAPI.getAll(suiteId ? parseInt(suiteId) : undefined)
  )

  const createMutation = useMutation(
    (data: any) => casesAPI.create({ ...data, suite_id: parseInt(suiteId!) }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['cases', suiteId])
        toast.success('Test case created successfully')
        handleCloseDialog()
      },
      onError: () => toast.error('Failed to create test case'),
    }
  )

  const deleteMutation = useMutation(
    (id: number) => casesAPI.delete(id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['cases', suiteId])
        toast.success('Test case deleted successfully')
      },
      onError: () => toast.error('Failed to delete test case'),
    }
  )

  const handleOpenDialog = (testCase?: any) => {
    if (testCase) {
      setEditingCase(testCase)
      setFormData({
        name: testCase.name,
        description: testCase.description || '',
        test_code: testCase.test_code,
        test_type: testCase.test_type,
        priority: testCase.priority,
        tags: testCase.tags?.join(', ') || '',
      })
    } else {
      setEditingCase(null)
      setFormData({
        name: '',
        description: '',
        test_code: '',
        test_type: 'api',
        priority: 'medium',
        tags: '',
      })
    }
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setEditingCase(null)
  }

  const handleSubmit = () => {
    if (!formData.name || !formData.test_code) {
      toast.error('Name and test code are required')
      return
    }
    
    const data = {
      ...formData,
      tags: formData.tags.split(',').map(t => t.trim()).filter(t => t),
    }
    
    createMutation.mutate(data)
  }

  if (isLoading) {
    return <Typography>Loading...</Typography>
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/suites')}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4">Test Cases</Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Test Case
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Tags</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cases?.data?.map((testCase: any) => (
              <TableRow key={testCase.id}>
                <TableCell>{testCase.name}</TableCell>
                <TableCell>
                  <Chip label={testCase.test_type} size="small" />
                </TableCell>
                <TableCell>
                  <Chip
                    label={testCase.priority}
                    color={
                      testCase.priority === 'critical'
                        ? 'error'
                        : testCase.priority === 'high'
                        ? 'warning'
                        : 'default'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {testCase.tags?.map((tag: string) => (
                    <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                  ))}
                </TableCell>
                <TableCell>
                  <Chip
                    label={testCase.is_active ? 'Active' : 'Inactive'}
                    color={testCase.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(testCase)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => deleteMutation.mutate(testCase.id)}
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
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCase ? 'Edit Test Case' : 'Create Test Case'}
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
            rows={2}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Test Code"
            multiline
            rows={6}
            value={formData.test_code}
            onChange={(e) => setFormData({ ...formData, test_code: e.target.value })}
            margin="normal"
            placeholder="def test_example():&#10;    assert True"
          />
          <Box display="flex" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Test Type</InputLabel>
              <Select
                value={formData.test_type}
                onChange={(e) => setFormData({ ...formData, test_type: e.target.value })}
              >
                <MenuItem value="api">API Testing</MenuItem>
                <MenuItem value="ui">UI Testing</MenuItem>
                <MenuItem value="db">Database Testing</MenuItem>
                <MenuItem value="security">Security Testing</MenuItem>
                <MenuItem value="performance">Performance Testing</MenuItem>
                <MenuItem value="mobile">Mobile Testing</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <TextField
            fullWidth
            label="Tags (comma-separated)"
            value={formData.tags}
            onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
            margin="normal"
            placeholder="smoke, regression, api"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingCase ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}