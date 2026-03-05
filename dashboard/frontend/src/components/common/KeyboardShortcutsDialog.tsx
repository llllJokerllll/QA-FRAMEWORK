import {
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import { Keyboard as KeyboardIcon } from '@mui/icons-material';

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onClose: () => void;
}

const shortcuts = [
  { key: '/', description: 'Focus search bar', category: 'Navigation' },
  { key: 'n', description: 'Create new test', category: 'Actions' },
  { key: 'h', description: 'Go to home/dashboard', category: 'Navigation' },
  { key: '?', description: 'Show this help dialog', category: 'Help' },
  { key: 'Esc', description: 'Close dialogs', category: 'Navigation' },
];

export default function KeyboardShortcutsDialog({
  open,
  onClose,
}: KeyboardShortcutsDialogProps) {
  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, typeof shortcuts>);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <KeyboardIcon color="primary" />
          <Typography variant="h6" fontWeight="bold">
            Keyboard Shortcuts
          </Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="textSecondary" mb={2}>
          Use keyboard shortcuts to navigate faster. Press the key combination to trigger the action.
        </Typography>

        {Object.entries(groupedShortcuts).map(([category, items]) => (
          <Box key={category} mb={3}>
            <Typography variant="subtitle2" color="primary" fontWeight="bold" mb={1}>
              {category}
            </Typography>
            <List dense disablePadding>
              {items.map((shortcut, index) => (
                <ListItem key={index} sx={{ px: 0 }}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
                    <ListItemText
                      primary={shortcut.description}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                    <Chip
                      label={shortcut.key}
                      size="small"
                      sx={{
                        fontFamily: 'monospace',
                        fontWeight: 'bold',
                        minWidth: 40,
                        backgroundColor: 'grey.100',
                      }}
                    />
                  </Box>
                </ListItem>
              ))}
            </List>
          </Box>
        ))}

        <Box mt={3} p={2} bgcolor="grey.50" borderRadius={1}>
          <Typography variant="caption" color="textSecondary">
            💡 Tip: Shortcuts are disabled when typing in input fields (except Esc)
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  );
}
