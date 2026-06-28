function relevancePercent(score) {
  // Cohere's rerank relevance_score is already a 0-1 probability —
  // no clamping/rescaling needed, unlike the old local cross-encoder's
  // unbounded logit scores.
  return Math.round(score * 100);
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
