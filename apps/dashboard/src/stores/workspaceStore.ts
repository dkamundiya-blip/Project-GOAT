import { create } from 'zustand';
import { WorkspaceConfig, SymbolName } from '../types/state';

interface WorkspaceStoreState {
  currentWorkspace: WorkspaceConfig;
  workspaces: WorkspaceConfig[];
  setWorkspace: (workspaceId: string) => void;
  setActiveSymbol: (symbol: SymbolName) => void;
}

const defaultWorkspaces: WorkspaceConfig[] = [
  { id: 'default', name: 'Master Research Workspace', activeSymbol: 'VOLATILITY_100', layoutPreset: 'default' },
  { id: 'scientific', name: 'Scientific Lineage Workspace', activeSymbol: 'BOOM_1000', layoutPreset: 'scientific' },
  { id: 'analytics', name: 'Microstructure Analytics Workspace', activeSymbol: 'STEP_INDEX', layoutPreset: 'analytics' },
];

export const useWorkspaceStore = create<WorkspaceStoreState>((set) => ({
  currentWorkspace: defaultWorkspaces[0],
  workspaces: defaultWorkspaces,
  setWorkspace: (workspaceId) =>
    set((state) => {
      const found = state.workspaces.find((w) => w.id === workspaceId);
      return found ? { currentWorkspace: found } : state;
    }),
  setActiveSymbol: (symbol) =>
    set((state) => ({
      currentWorkspace: { ...state.currentWorkspace, activeSymbol: symbol },
    })),
}));
