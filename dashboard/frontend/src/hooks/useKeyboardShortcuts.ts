import { useEffect, useCallback } from 'react';

interface KeyboardShortcut {
  key: string;
  action: () => void;
  description: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
}

/**
 * Custom hook for keyboard shortcuts
 * @param shortcuts Array of keyboard shortcuts to register
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const activeElement = document.activeElement;
      const isInput =
        activeElement instanceof HTMLInputElement ||
        activeElement instanceof HTMLTextAreaElement ||
        activeElement?.getAttribute('contenteditable') === 'true';

      if (isInput) {
        return;
      }

      // Check each shortcut
      for (const shortcut of shortcuts) {
        const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey : !event.ctrlKey;
        const shiftMatch = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.altKey ? event.altKey : !event.altKey;

        if (keyMatch && ctrlMatch && shiftMatch && altMatch) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);
}

/**
 * Default keyboard shortcuts for QA-FRAMEWORK
 */
export const DEFAULT_SHORTCUTS = [
  {
    key: '/',
    description: 'Focus search',
    category: 'Navigation',
  },
  {
    key: 'n',
    description: 'New test/test suite',
    category: 'Actions',
  },
  {
    key: 'h',
    description: 'Go to home',
    category: 'Navigation',
  },
  {
    key: '?',
    description: 'Show keyboard shortcuts',
    category: 'Help',
  },
  {
    key: 'Escape',
    description: 'Close dialog/modal',
    category: 'Navigation',
  },
];
