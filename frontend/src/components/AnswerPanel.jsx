import ResultCard from "./ResultCard.jsx";

function renderAnswerWithCitations(text) {
  const parts = text.split(/(\[Source \d+\])/g);
  return parts.map((part, i) => {
    const match = part.match(/^\[Source (\d+)\]$/);
    if (match) {
      return (
        <span className="citation-chip" key={i}>
          {match[1]}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

export default function AnswerPanel({ answer, sources }) {
  return (
    <div className="answer-panel">
      <p className="answer-text">{renderAnswerWithCitations(answer)}</p>

      {sources?.length > 0 && (
        <div className="sources">
          <h3 className="sources-heading">Sources</h3>
          {sources.map((s, i) => (
            <ResultCard result={s} index={i} key={s.idx} />
          ))}
        </div>
      )}
    </div>
  );
}
