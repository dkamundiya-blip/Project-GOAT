import { useLayoutStore } from '../stores/layoutStore';
import { useSidebarStore } from '../stores/sidebarStore';
import { useInspectorStore } from '../stores/inspectorStore';

export function useLayout() {
  const layout = useLayoutStore();
  const sidebar = useSidebarStore();
  const inspector = useInspectorStore();

  return {
    ...layout,
    sidebarCollapsed: sidebar.collapsed,
    toggleSidebar: sidebar.toggle,
    inspectorOpen: inspector.isOpen,
    toggleInspector: inspector.toggleInspector,
  };
}
