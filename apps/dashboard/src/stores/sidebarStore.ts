import { create } from 'zustand';
import { SidebarState } from '../types/layout';

interface SidebarStoreState {
  state: SidebarState;
  collapsed: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

export const useSidebarStore = create<SidebarStoreState>((set) => ({
  state: 'expanded',
  collapsed: false,
  toggle: () => set((s) => ({ collapsed: !s.collapsed, state: s.collapsed ? 'expanded' : 'collapsed' })),
  setCollapsed: (collapsed) => set({ collapsed, state: collapsed ? 'collapsed' : 'expanded' }),
}));
