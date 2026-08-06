import { useThemeStore } from '../stores/themeStore';

export function useTheme() {
  const { theme, setTheme, toggleTheme } = useThemeStore();
  return { theme, setTheme, toggleTheme, isDark: theme === 'dark' };
}
