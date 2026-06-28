import { useState, useRef, useEffect } from "react";
import "./App.css";

import { Header } from "./components/Header";
import { SymbolBar } from "./components/SymbolBar";
import { TruthTable } from "./components/TruthTable";
import { Footer } from "./components/Footer";

interface HistoryItem {
  expr: string;
  headers: string[];
  rows: string[][];
}

function App() {
  const [expr, setExpr] = useState<string>("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [dark, setDark] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const toggleTheme = () => {
    setDark( !dark );
    document.body.classList.toggle("light", !dark);
  }

  useEffect(() => {
    toggleTheme();
  }, [])

  const insertSymbol = (sym: string) => {
    const input = inputRef.current;
    if (!input) return;
    const start = input.selectionStart ?? expr.length;
    const end = input.selectionEnd ?? expr.length;
    const next = expr.slice(0, start) + sym + expr.slice(end);
    setExpr(next);
    requestAnimationFrame(() => {
      input.focus();
      input.setSelectionRange(start + sym.length, start + sym.length);
    });
  };

  const evaluateExpr = async () => {
    if (!expr) return;
    setLoading(true);
    setError(null)

    try {
      const res = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expression: expr }),
      });
      const data = await res.json();

      if (data.error) {
        setError(String(data.error));
      } else {
        setHistory((prev) => [{ expr, ...data }, ...prev]);
        setExpr("");
      }
    } catch (err) {
      setError(String(error))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Header dark={dark} onToggle={toggleTheme} />
      <SymbolBar onInsert={insertSymbol} />
      <div className="input-area">
        <div className="input-wrap">
          <input
            type="text"
            ref={inputRef}
            value={expr}
            placeholder="e.g. (p∨¬q)→(¬p∧q)"
            autoComplete="off"
            onChange={(e) => setExpr(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && evaluateExpr()}
          />
        </div>
        <button disabled={loading} onClick={evaluateExpr}>
          Evaluate
        </button>
      </div>

      {error && (
        <div className="result">
          <div className="error">Error: {error}</div>
        </div>
      )}

      {loading && (
        <div className="result">
          <span className="spinner"></span> Evaluating...
        </div>
      )}

      {history.map((item, i) => (
        <TruthTable
          key={i}
          expression={item.expr}
          headers={item.headers}
          rows={item.rows}
        />
      ))}
      <Footer />
    </>
  );
}

export default App;