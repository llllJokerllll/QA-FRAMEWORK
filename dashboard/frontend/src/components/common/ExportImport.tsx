import { useState } from 'react'
import {
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Snackbar,
  Alert,
  Box,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Download,
  Upload,
  TableChart,
  Code,
  PictureAsPdf,
  CloudDownload,
  CloudUpload,
} from '@mui/icons-material'

interface ExportImportProps {
  onExport: (format: 'csv' | 'json' | 'pdf') => Promise<void>
  onImport: (file: File, format: 'csv' | 'json') => Promise<void>
  exportLabel?: string
  importLabel?: string
}

export default function ExportImport({
  onExport,
  onImport,
  exportLabel = 'Export',
  importLabel = 'Import',
}: ExportImportProps) {
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null)
  const [importAnchorEl, setImportAnchorEl] = useState<null | HTMLElement>(null)
  const [loading, setLoading] = useState(false)
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  })

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportAnchorEl(event.currentTarget)
  }

  const handleImportClick = (event: React.MouseEvent<HTMLElement>) => {
    setImportAnchorEl(event.currentTarget)
  }

  const handleClose = () => {
    setExportAnchorEl(null)
    setImportAnchorEl(null)
  }

  const handleExport = async (format: 'csv' | 'json' | 'pdf') => {
    setLoading(true)
    handleClose()
    try {
      await onExport(format)
      setSnackbar({
        open: true,
        message: `Successfully exported to ${format.toUpperCase()}`,
        severity: 'success',
      })
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        severity: 'error',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const format = file.name.endsWith('.csv') ? 'csv' : 'json'
    setLoading(true)
    handleClose()
    try {
      await onImport(file, format)
      setSnackbar({
        open: true,
        message: `Successfully imported ${file.name}`,
        severity: 'success',
      })
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        severity: 'error',
      })
    } finally {
      setLoading(false)
      // Reset input
      event.target.value = ''
    }
  }

  return (
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
      {/* Export Button */}
      <Tooltip title="Export data">
        <Button
          variant="outlined"
          size="small"
          startIcon={loading ? <CircularProgress size={16} /> : <CloudDownload />}
          onClick={handleExportClick}
          disabled={loading}
        >
          {exportLabel}
        </Button>
      </Tooltip>
      <Menu
        anchorEl={exportAnchorEl}
        open={Boolean(exportAnchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={() => handleExport('csv')}>
          <ListItemIcon>
            <TableChart />
          </ListItemIcon>
          <ListItemText>Export as CSV</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleExport('json')}>
          <ListItemIcon>
            <Code />
          </ListItemIcon>
          <ListItemText>Export as JSON</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleExport('pdf')}>
          <ListItemIcon>
            <PictureAsPdf />
          </ListItemIcon>
          <ListItemText>Export as PDF</ListItemText>
        </MenuItem>
      </Menu>

      {/* Import Button */}
      <Tooltip title="Import data">
        <Button
          variant="outlined"
          size="small"
          startIcon={<CloudUpload />}
          onClick={handleImportClick}
          disabled={loading}
        >
          {importLabel}
        </Button>
      </Tooltip>
      <Menu
        anchorEl={importAnchorEl}
        open={Boolean(importAnchorEl)}
        onClose={handleClose}
      >
        <MenuItem component="label">
          <ListItemIcon>
            <TableChart />
          </ListItemIcon>
          <ListItemText>Import from CSV</ListItemText>
          <input
            type="file"
            accept=".csv"
            hidden
            onChange={handleFileSelect}
          />
        </MenuItem>
        <MenuItem component="label">
          <ListItemIcon>
            <Code />
          </ListItemIcon>
          <ListItemText>Import from JSON</ListItemText>
          <input
            type="file"
            accept=".json"
            hidden
            onChange={handleFileSelect}
          />
        </MenuItem>
      </Menu>

      {/* Snackbar for feedback */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}
