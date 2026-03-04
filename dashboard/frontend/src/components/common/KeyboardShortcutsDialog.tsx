import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Divider,
} from '@mui/material'
import {
  Keyboard as KeyboardIcon,
} from '@mui/icons-material'

interface ShortcutItem {
  key: string
  description: string
}

interface KeyboardShortcutsDialogProps {
  open: boolean
  onClose: () => void
}

const shortcuts: ShortcutItem[] = [
  { key: '/', description: 'Focus search input' },
  { key: 'n', description: 'Navigate to Test Suites' },
  { key: 'h', description: 'Navigate to Home/Dashboard' },
  { key: '?', description: 'Show this help dialog' },
  { key: 'Escape', description: 'Close dialog' },
]

export default function KeyboardShortcutsDialog({ open, onClose }: KeyboardShortcutsDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <KeyboardIcon />
          <Typography variant="h6">Keyboard Shortcuts</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" paragraph>
          Power user keyboard shortcuts to navigate the application faster.
        </Typography>

        <Divider sx={{ my: 2 }} />

        <Table>
          <TableBody>
            {shortcuts.map((shortcut) => (
              <TableRow key={shortcut.key}>
                <TableCell sx={{ width: '30%', pb: 1, pt: 1 }}>
                  <Chip
                    label={shortcut.key}
                    variant="outlined"
                    sx={{
                      fontFamily: 'monospace',
                      fontWeight: 'bold',
                      fontSize: '0.875rem',
                    }}
                  />
                </TableCell>
                <TableCell sx={{ pb: 1, pt: 1 }}>
                  <Typography variant="body2">{shortcut.description}</Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <Divider sx={{ my: 2 }} />

        <Typography variant="caption" color="text.secondary" display="block">
          Press <strong>Escape</strong> or click outside to close this dialog
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Got it!
        </Button>
      </DialogActions>
    </Dialog>
  )
}
