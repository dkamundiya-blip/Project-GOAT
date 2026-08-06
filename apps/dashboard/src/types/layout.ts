export type ThemeMode = 'dark' | 'light' | 'system';

export type SidebarState = 'expanded' | 'collapsed' | 'hidden';

export type InspectorState = 'open' | 'closed';

export interface LayoutConfig {
  sidebarState: SidebarState;
  inspectorState: InspectorState;
  topNavVisible: boolean;
  bottomStatusVisible: boolean;
}
