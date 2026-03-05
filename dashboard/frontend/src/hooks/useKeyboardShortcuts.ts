import { useEffect, useCallback } from 'react';

export interface KeyboardShortcut {
  key: string;
  description: string;
  action: () => void;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
}

interface UseKeyboardShortcutsProps {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
}

/**
 * Custom hook for handling keyboard shortcuts
 *
 * @param shortcuts - Array of keyboard shortcuts to register
 * @param enabled - Whether shortcuts are enabled (default: true)
 *
 * @example
 * useKeyboardShortcuts({
 *   shortcuts: [
 *     { key: '/', description: 'Focus search', action: () => searchInput.focus() },
 *     { key: 'n', description: 'New test', action: () => navigate('/tests/new') },
 *   ]
 * });
 */
export function useKeyboardShortcuts({
  shortcuts,
  enabled = true,
}: UseKeyboardShortcutsProps) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Ignore shortcuts when typing in inputs
      const target = event.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        // Allow Escape key even in inputs
        if (event.key !== 'Escape') {
          return;
        }
      }

      // Find matching shortcut
      const matchingShortcut = shortcuts.find((shortcut) => {
        const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase();
        const ctrlMatches = shortcut.ctrl ? event.ctrlKey || event.metaKey : !event.ctrlKey && !event.metaKey;
        const shiftMatches = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatches = shortcut.alt ? event.altKey : !event.altKey;

        return keyMatches && ctrlMatches && shiftMatches && altMatches;
      });

      if (matchingShortcut) {
        event.preventDefault();
        matchingShortcut.action();
      }
    },
    [shortcuts, enabled]
  );

  useEffect(() => {
    if (enabled) {
      document.addEventListener('keydown', handleKeyDown);
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [handleKeyDown, enabled]);

  return { shortcuts };
}
