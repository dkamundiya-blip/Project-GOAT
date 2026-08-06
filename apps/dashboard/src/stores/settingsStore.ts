/**
 * Project GOAT v1.0 — Dashboard Workstation Settings Store
 */

import { create } from 'zustand';

interface SettingsState {
  themeMode: 'dark' | 'light';
  refreshIntervalMs: number;
  notificationSound: boolean;
  compactMode: boolean;
  setThemeMode: (mode: 'dark' | 'light') => void;
  setRefreshInterval: (ms: number) => void;
  toggleNotificationSound: () => void;
  toggleCompactMode: () => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  themeMode: 'dark',
  refreshIntervalMs: 5000,
  notificationSound: true,
  compactMode: false,
  setThemeMode: (themeMode) => set({ themeMode }),
  setRefreshInterval: (refreshIntervalMs) => set({ refreshIntervalMs }),
  toggleNotificationSound: () => set((state) => ({ notificationSound: !state.notificationSound })),
  toggleCompactMode: () => set((state) => ({ compactMode: !state.compactMode })),
}));
