import { useSymbolStore } from '../stores/symbolStore';

export function useSymbol() {
  const { currentSymbol, setSymbol, availableSymbols } = useSymbolStore();
  return { currentSymbol, setSymbol, availableSymbols };
}
