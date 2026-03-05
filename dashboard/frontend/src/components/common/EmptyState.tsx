import { Box, Typography, Button } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface EmptyStateProps {
  illustration: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  illustration,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
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
      {/* Illustration */}
      <Box
        component="img"
        src={illustration}
        alt={title}
        sx={{
          width: '100%',
          maxWidth: '300px',
          height: 'auto',
          mb: 3,
          opacity: 0.8,
        }}
        onError={(e) => {
          // Fallback if image doesn't load
          e.currentTarget.style.display = 'none';
        }}
      />

      {/* Title */}
      <Typography variant="h5" gutterBottom fontWeight="bold">
        {title}
      </Typography>

      {/* Description */}
      <Typography
        variant="body1"
        color="textSecondary"
        sx={{ maxWidth: '500px', mb: 3 }}
      >
        {description}
      </Typography>

      {/* Action Button */}
      {actionLabel && onAction && (
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<AddIcon />}
          onClick={onAction}
          sx={{ mt: 2 }}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}
