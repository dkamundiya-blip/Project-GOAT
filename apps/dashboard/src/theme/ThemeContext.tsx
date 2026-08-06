import React, { createContext, useContext, useState, useEffect } from 'react';
import { tokens } from './tokens';

export type ThemeMode = 'dark' | 'high-contrast';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
  setMode: (mode: ThemeMode) => void;
  tokens: typeof tokens;
  reducedMotion: boolean;
}

export const ThemeContext = createContext<ThemeContextType>({
  mode: 'dark',
  toggleTheme: () => {},
  setMode: () => {},
  tokens,
  reducedMotion: false,
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setModeState] = useState<ThemeMode>('dark');
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReducedMotion(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const toggleTheme = () => {
    setModeState((prev) => (prev === 'dark' ? 'high-contrast' : 'dark'));
  };

  const setMode = (newMode: ThemeMode) => {
    setModeState(newMode);
  };

  return (
    <ThemeContext.Provider value={{ mode, toggleTheme, setMode, tokens, reducedMotion }}>
      <div className={`theme-${mode} min-h-screen text-slate-100 bg-[#06090e] font-sans antialiased selection:bg-cyan-500 selection:text-black`}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
