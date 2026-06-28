export default function ModeToggle({ mode, onChange }) {
  return (
    <div className="mode-toggle" role="tablist" aria-label="Search mode">
      <button
        role="tab"
        aria-selected={mode === "search"}
        className={mode === "search" ? "active" : ""}
        onClick={() => onChange("search")}
      >
        Search passages
      </button>
      <button
        role="tab"
        aria-selected={mode === "ask"}
        className={mode === "ask" ? "active" : ""}
        onClick={() => onChange("ask")}
      >
        Ask a question
      </button>
    </div>
  );
}
