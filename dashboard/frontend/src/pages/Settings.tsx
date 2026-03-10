import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Grid,
  Radio,
  RadioGroup,
  FormControl,
  FormLabel,
  Paper,
} from '@mui/material'
import {
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon,
  SettingsBrightness as SystemModeIcon,
} from '@mui/icons-material'
import useAuthStore from '../stores/authStore'
import { useThemeContext, ThemeMode } from '../theme'

export default function Settings() {
  const { user } = useAuthStore()
  const { mode, actualMode, setMode } = useThemeContext()
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' })
  
  // Profile settings
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [email, setEmail] = useState(user?.email || '')
  
  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [testFailureAlerts, setTestFailureAlerts] = useState(true)
  const [weeklyReports, setWeeklyReports] = useState(false)
  
  // Appearance settings
  const [compactMode, setCompactMode] = useState(false)

  // Sync theme mode from context
  const [themeMode, setThemeMode] = useState<ThemeMode>(mode)

  useEffect(() => {
    setThemeMode(mode)
  }, [mode])

  const handleThemeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newMode = event.target.value as ThemeMode
    setThemeMode(newMode)
    setMode(newMode)
    setSnackbar({ open: true, message: `Theme changed to ${newMode} mode`, severity: 'success' })
  }

  const handleSaveProfile = () => {
    // TODO: Implement profile update API call
    setSnackbar({ open: true, message: 'Profile updated successfully!', severity: 'success' })
  }

  const handleSaveNotifications = () => {
    // TODO: Implement notification settings update
    setSnackbar({ open: true, message: 'Notification settings saved!', severity: 'success' })
  }

  const handleSaveAppearance = () => {
    // Theme is already saved via handleThemeChange
    setSnackbar({ open: true, message: 'Appearance settings saved!', severity: 'success' })
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {/* Profile Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PersonIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Profile Settings</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Username"
                value={user?.username || ''}
                disabled
                helperText="Username cannot be changed"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button variant="contained" onClick={handleSaveProfile}>
                Save Profile
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <NotificationsIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Notification Settings</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <FormControlLabel
            control={
              <Switch
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
              />
            }
            label="Email Notifications"
          />
          <br />
          <FormControlLabel
            control={
              <Switch
                checked={testFailureAlerts}
                onChange={(e) => setTestFailureAlerts(e.target.checked)}
              />
            }
            label="Test Failure Alerts"
          />
          <br />
          <FormControlLabel
            control={
              <Switch
                checked={weeklyReports}
                onChange={(e) => setWeeklyReports(e.target.checked)}
              />
            }
            label="Weekly Reports"
          />
          <br />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" onClick={handleSaveNotifications}>
              Save Notifications
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Appearance Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <PaletteIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Appearance</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
              />
            }
            label="Dark Mode"
          />
          <br />
          <FormControlLabel
            control={
              <Switch
                checked={compactMode}
                onChange={(e) => setCompactMode(e.target.checked)}
              />
            }
            label="Compact Mode"
          />
          <br />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" onClick={handleSaveAppearance}>
              Save Appearance
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Account Info */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <SecurityIcon sx={{ mr: 1 }} />
            <Typography variant="h6">Account Information</Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          
          <Typography variant="body2" color="textSecondary">
            <strong>Subscription:</strong> {user?.subscription_plan || 'Free'}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            <strong>Status:</strong> {user?.subscription_status || 'Active'}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            <strong>Role:</strong> {user?.is_superuser ? 'Admin' : 'User'}
          </Typography>
        </CardContent>
      </Card>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}
