import { useState } from "react";
import ModeToggle from "./components/ModeToggle.jsx";
import SearchBar from "./components/SearchBar.jsx";
import ResultCard from "./components/ResultCard.jsx";
import AnswerPanel from "./components/AnswerPanel.jsx";
import { search, ask } from "./api.js";

export default function App() {
  const [mode, setMode] = useState("ask");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [answer, setAnswer] = useState(null);

  async function handleSubmit(query) {
    setLoading(true);
    setError(null);
    setResults(null);
    setAnswer(null);

    try {
      if (mode === "ask") {
        const data = await ask(query, 5);
        setAnswer(data);
      } else {
        const data = await search(query, 5);
        setResults(data.results);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleModeChange(next) {
    setMode(next);
    setResults(null);
    setAnswer(null);
    setError(null);
  }

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">NLP textbook · ch.8 transformers</p>
        <h1>Ask the chapter anything</h1>
        <p className="subtitle">
          Semantic search and grounded answers over the transformers chapter —
          hybrid retrieval, cross-encoder reranking, and citation-backed
          generation.
        </p>
      </header>

      <ModeToggle mode={mode} onChange={handleModeChange} />
      <SearchBar onSubmit={handleSubmit} loading={loading} mode={mode} />

      <main className="results-area">
        {error && (
          <div className="empty-state error">
            <p>Something went wrong: {error}</p>
            <p className="hint">
              Check that the backend is running at the configured API URL.
            </p>
          </div>
        )}

        {!error && !loading && !results && !answer && (
          <div className="empty-state">
            <p>Nothing here yet.</p>
            <p className="hint">
              Try asking something about multi-head attention, layer norm, or
              the KV cache.
            </p>
          </div>
        )}

        {mode === "search" && results && (
          <div className="result-list">
            {results.map((r, i) => (
              <ResultCard result={r} index={i} key={r.idx} />
            ))}
          </div>
        )}

        {mode === "ask" && answer && (
          <AnswerPanel answer={answer.answer} sources={answer.sources} />
        )}
      </main>
    </div>
  );
}
