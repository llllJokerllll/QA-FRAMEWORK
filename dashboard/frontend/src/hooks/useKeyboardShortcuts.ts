import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

interface KeyboardShortcutsCallbacks {
  onHelpToggle?: () => void
}

export function useKeyboardShortcuts(callbacks?: KeyboardShortcutsCallbacks) {
  const navigate = useNavigate()
  const [isHelpOpen, setIsHelpOpen] = useState(false)

  const toggleHelp = useCallback(() => {
    setIsHelpOpen((prev) => !prev)
    callbacks?.onHelpToggle?.()
  }, [callbacks])

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Ignore if user is typing in an input, textarea, or contenteditable
      const target = event.target as HTMLElement
      const isInputField =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.isContentEditable

      if (isInputField) {
        // Only allow '?' to work in input fields for help
        if (event.key === '?') {
          event.preventDefault()
          toggleHelp()
        }
        return
      }

      switch (event.key) {
        case '/':
          // Focus search
          event.preventDefault()
          const searchInput = document.querySelector<HTMLInputElement>(
            'input[placeholder*="search"], input[type="search"]'
          )
          if (searchInput) {
            searchInput.focus()
          } else {
            // Fallback to first input
            const firstInput = document.querySelector('input') as HTMLInputElement
            firstInput?.focus()
          }
          break

        case 'n':
          // New suite
          event.preventDefault()
          navigate('/suites')
          break

        case 'h':
          // Home
          event.preventDefault()
          navigate('/')
          break

        case '?':
          // Show shortcuts help
          event.preventDefault()
          toggleHelp()
          break

        case 'Escape':
          // Close help dialog
          if (isHelpOpen) {
            event.preventDefault()
            toggleHelp()
          }
          break
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [navigate, isHelpOpen, toggleHelp])

  return {
    isHelpOpen,
    toggleHelp,
  }
}
