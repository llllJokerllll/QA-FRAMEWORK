import { Box, Typography, Button, useTheme } from '@mui/material'

interface EmptyStateProps {
  illustration: string
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export default function EmptyState({
  illustration,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        textAlign: 'center',
        p: 4,
      }}
    >
      <Box
        component="img"
        src={illustration}
        alt={title}
        sx={{
          width: 300,
          height: 200,
          maxWidth: '100%',
          mb: 3,
          opacity: 0.8,
        }}
      />
      <Typography variant="h5" gutterBottom color="text.primary">
        {title}
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ maxWidth: 500, mb: actionLabel ? 3 : 0 }}
      >
        {description}
      </Typography>
      {actionLabel && onAction && (
        <Button
          variant="contained"
          onClick={onAction}
          size="large"
          sx={{
            textTransform: 'none',
            px: 4,
            py: 1.5,
          }}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  )
}
