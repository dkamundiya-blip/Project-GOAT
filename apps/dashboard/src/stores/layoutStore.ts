import { create } from 'zustand';
import { LayoutConfig, SidebarState, InspectorState } from '../types/layout';

interface LayoutStoreState extends LayoutConfig {
  setSidebarState: (state: SidebarState) => void;
  setInspectorState: (state: InspectorState) => void;
  toggleTopNav: () => void;
  toggleBottomStatus: () => void;
  resetLayout: () => void;
}

const defaultLayout: LayoutConfig = {
  sidebarState: 'expanded',
  inspectorState: 'closed',
  topNavVisible: true,
  bottomStatusVisible: true,
};

export const useLayoutStore = create<LayoutStoreState>((set) => ({
  ...defaultLayout,
  setSidebarState: (sidebarState) => set({ sidebarState }),
  setInspectorState: (inspectorState) => set({ inspectorState }),
  toggleTopNav: () => set((state) => ({ topNavVisible: !state.topNavVisible })),
  toggleBottomStatus: () => set((state) => ({ bottomStatusVisible: !state.bottomStatusVisible })),
  resetLayout: () => set(defaultLayout),
}));
