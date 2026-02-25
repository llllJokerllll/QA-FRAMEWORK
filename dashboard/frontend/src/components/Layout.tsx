import { ReactNode } from 'react'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Folder as FolderIcon,
  PlayArrow as PlayArrowIcon,
  Payment as PaymentIcon,
  AutoFixHigh as AutoFixHighIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../stores/authStore'

const drawerWidth = 240

interface LayoutProps {
  children: ReactNode
  sidebarOpen: boolean
  onSidebarToggle: () => void
}

export default function Layout({ children, sidebarOpen, onSidebarToggle }: LayoutProps) {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Test Suites', icon: <FolderIcon />, path: '/suites' },
    { text: 'Executions', icon: <PlayArrowIcon />, path: '/executions' },
    { text: 'Self-Healing', icon: <AutoFixHighIcon />, path: '/self-healing' },
    { text: 'Billing', icon: <PaymentIcon />, path: '/billing' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: sidebarOpen ? `${drawerWidth}px` : 0,
          transition: 'all 0.3s',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={onSidebarToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            QA Framework Dashboard
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.username}
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
      >
        <Toolbar />
        <Divider />
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton onClick={() => navigate(item.path)}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
        <List>
          <ListItem disablePadding>
            <ListItemButton>
              <ListItemIcon>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText primary="Settings" />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          width: sidebarOpen ? `calc(100% - ${drawerWidth}px)` : '100%',
          ml: sidebarOpen ? `${drawerWidth}px` : 0,
          transition: 'all 0.3s',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  )
}