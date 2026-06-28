const SYMBOLS = ["¬", "∧", "∨", "→", "↔"] as const;

type Symbol = (typeof SYMBOLS)[number];

interface SymbolBarProps {
  onInsert: (symbol: Symbol) => void;
}

export const SymbolBar = ({ onInsert }: SymbolBarProps) => {
  return (
    <div className="symbols">
      <span>insert:</span>
      {SYMBOLS.map((sym) => (
        <button key={sym} className="sym-btn" onClick={() => onInsert(sym)}>
          {sym}
        </button>
      ))}
    </div>
  );
};