import { create } from 'zustand';

interface InspectorStoreState {
  isOpen: boolean;
  title: string;
  content: string | null;
  openInspector: (title: string, content?: string | null) => void;
  closeInspector: () => void;
  toggleInspector: () => void;
}

export const useInspectorStore = create<InspectorStoreState>((set) => ({
  isOpen: false,
  title: 'Inspector',
  content: null,
  openInspector: (title, content = null) => set({ isOpen: true, title, content }),
  closeInspector: () => set({ isOpen: false }),
  toggleInspector: () => set((state) => ({ isOpen: !state.isOpen })),
}));
