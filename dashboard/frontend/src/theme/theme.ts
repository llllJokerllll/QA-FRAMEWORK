import { createTheme, ThemeOptions } from '@mui/material/styles'

// Design tokens - CSS variables approach for consistency
export const designTokens = {
  colors: {
    // Primary brand colors
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
    // Secondary/accent colors
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#ffffff',
    },
    // Status colors
    success: {
      main: '#2e7d32',
      light: '#4caf50',
      dark: '#1b5e20',
    },
    warning: {
      main: '#ed6c02',
      light: '#ff9800',
      dark: '#e65100',
    },
    error: {
      main: '#d32f2f',
      light: '#ef5350',
      dark: '#c62828',
    },
    info: {
      main: '#0288d1',
      light: '#03a9f4',
      dark: '#01579b',
    },
  },
  // Typography
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 600 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
    h4: { fontSize: '1.5rem', fontWeight: 500 },
    h5: { fontSize: '1.25rem', fontWeight: 500 },
    h6: { fontSize: '1rem', fontWeight: 500 },
  },
  // Spacing and border radius
  shape: {
    borderRadius: 8,
  },
  // Transitions
  transitions: {
    themeChange: 'background-color 0.3s ease, color 0.2s ease',
  },
}

// Light theme configuration
const lightThemeOptions: ThemeOptions = {
  palette: {
    mode: 'light',
    primary: designTokens.colors.primary,
    secondary: designTokens.colors.secondary,
    success: designTokens.colors.success,
    warning: designTokens.colors.warning,
    error: designTokens.colors.error,
    info: designTokens.colors.info,
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
    divider: 'rgba(0, 0, 0, 0.12)',
  },
  typography: designTokens.typography,
  shape: designTokens.shape,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: designTokens.colors.primary.main,
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#ffffff',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          transition: designTokens.transitions.themeChange,
        },
      },
    },
  },
}

// Dark theme configuration
const darkThemeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      ...designTokens.colors.primary,
      main: '#90caf9', // Lighter blue for dark mode contrast
    },
    secondary: {
      ...designTokens.colors.secondary,
      main: '#ce93d8', // Lighter purple for dark mode contrast
    },
    success: {
      main: '#66bb6a',
      light: '#81c784',
      dark: '#4caf50',
    },
    warning: {
      main: '#ffa726',
      light: '#ffb74d',
      dark: '#ff9800',
    },
    error: {
      main: '#ef5350',
      light: '#e57373',
      dark: '#f44336',
    },
    info: {
      main: '#29b6f6',
      light: '#4fc3f7',
      dark: '#03a9f4',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: 'rgba(255, 255, 255, 0.87)',
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
  },
  typography: designTokens.typography,
  shape: designTokens.shape,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.4)',
          backgroundColor: '#1e1e1e',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1e1e1e',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          transition: designTokens.transitions.themeChange,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          },
        },
      },
    },
  },
}

// Create and export themes
export const lightTheme = createTheme(lightThemeOptions)
export const darkTheme = createTheme(darkThemeOptions)

// Theme type for context
export type ThemeMode = 'light' | 'dark' | 'system'

// Helper to get system preference
export const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// Helper to get stored theme preference
export const getStoredTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'system'
  return (localStorage.getItem('themeMode') as ThemeMode) || 'system'
}

// Helper to store theme preference
export const setStoredTheme = (mode: ThemeMode): void => {
  if (typeof window === 'undefined') return
  localStorage.setItem('themeMode', mode)
}
