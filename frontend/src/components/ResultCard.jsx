function relevancePercent(score) {
  // Cross-encoder scores are unbounded logits (observed roughly -12 to +10 here).
  // Clamp and rescale to 0-100% purely so results are visually comparable to each other.
  const clamped = Math.max(-12, Math.min(10, score));
  return Math.round(((clamped + 12) / 22) * 100);
}

export default function ResultCard({ result, index }) {
  const pct = relevancePercent(result.score);

  return (
    <article className="result-card">
      <div className="result-meta">
        <span className="result-rank">#{index + 1}</span>
        <span className="result-page">p.{result.page}</span>
        <span className="result-score" title={`raw score ${result.score.toFixed(2)}`}>
          {result.score.toFixed(2)}
        </span>
      </div>
      <div className="relevance-bar" aria-hidden="true">
        <div className="relevance-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="result-text">{result.text}</p>
    </article>
  );
}
