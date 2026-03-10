import React from 'react'
import { Button, CircularProgress, SxProps, Theme } from '@mui/material'

interface LoadingButtonProps {
  loading?: boolean
  children: React.ReactNode
  onClick?: () => void
  variant?: 'text' | 'outlined' | 'contained'
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  fullWidth?: boolean
  sx?: SxProps<Theme>
  type?: 'button' | 'submit' | 'reset'
}

const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  children,
  onClick,
  variant = 'contained',
  color = 'primary',
  size = 'medium',
  disabled = false,
  fullWidth = false,
  sx,
  type = 'button',
}) => {
  return (
    <Button
      variant={variant}
      color={color}
      size={size}
      disabled={disabled || loading}
      fullWidth={fullWidth}
      onClick={onClick}
      type={type}
      sx={{
        position: 'relative',
        ...sx,
      }}
    >
      {loading && (
        <CircularProgress
          size={size === 'small' ? 16 : size === 'large' ? 24 : 20}
          sx={{
            position: 'absolute',
            left: '50%',
            marginLeft: '-12px',
          }}
        />
      )}
      <span style={{ opacity: loading ? 0 : 1 }}>{children}</span>
    </Button>
  )
}

export default LoadingButton
