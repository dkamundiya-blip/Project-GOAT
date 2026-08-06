import { create } from 'zustand';
import { SymbolName } from '../types/state';

interface SymbolStoreState {
  currentSymbol: SymbolName;
  availableSymbols: SymbolName[];
  setSymbol: (symbol: SymbolName) => void;
}

const defaultSymbols: SymbolName[] = [
  'VOLATILITY_10',
  'VOLATILITY_25',
  'VOLATILITY_50',
  'VOLATILITY_75',
  'VOLATILITY_100',
  'BOOM_500',
  'BOOM_1000',
  'CRASH_500',
  'CRASH_1000',
  'JUMP_10',
  'JUMP_25',
  'JUMP_50',
  'JUMP_75',
  'JUMP_100',
  'STEP_INDEX',
];

export const useSymbolStore = create<SymbolStoreState>((set) => ({
  currentSymbol: 'VOLATILITY_100',
  availableSymbols: defaultSymbols,
  setSymbol: (currentSymbol) => set({ currentSymbol }),
}));
