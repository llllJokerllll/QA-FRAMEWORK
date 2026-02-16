import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
} from '@mui/material'
import { useMutation } from 'react-query'
import { authAPI } from '../api/client'
import useAuthStore from '../stores/authStore'
import toast from 'react-hot-toast'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const loginMutation = useMutation(
    () => authAPI.login(username, password),
    {
      onSuccess: (response) => {
        const { access_token } = response.data
        // Get user info
        authAPI.getMe().then((userResponse) => {
          login(access_token, userResponse.data)
          toast.success('Login successful!')
          navigate('/')
        })
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Login failed')
      },
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!username || !password) {
      toast.error('Please fill in all fields')
      return
    }
    loginMutation.mutate()
  }

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ bgcolor: 'background.default' }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', mx: 2 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom align="center">
            QA Framework
          </Typography>
          <Typography variant="h6" gutterBottom align="center" color="textSecondary">
            Dashboard Login
          </Typography>

          {loginMutation.isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Invalid username or password
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              variant="outlined"
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loginMutation.isLoading}
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              variant="outlined"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loginMutation.isLoading}
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              sx={{ mt: 3 }}
              disabled={loginMutation.isLoading}
            >
              {loginMutation.isLoading ? 'Logging in...' : 'Login'}
            </Button>
          </form>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              Demo credentials: admin / admin123
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  )
}