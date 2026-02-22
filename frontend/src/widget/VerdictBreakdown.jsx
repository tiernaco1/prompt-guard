const VERDICTS = [
  { key: "BLOCKED",   label: "BLOCKED",   color: "var(--pg-blocked)" },
  { key: "SANITISED", label: "SANITISED", color: "var(--pg-sanitised)" },
  { key: "ALLOWED",   label: "ALLOWED",   color: "var(--pg-passed)" },
];

const VerdictBreakdown = ({ entries = [] }) => {
  const total = entries.length;
  const counts = { BLOCKED: 0, SANITISED: 0, ALLOWED: 0 };
  for (const entry of entries) {
    if (entry.action === "BLOCKED") counts.BLOCKED++;
    else if (entry.action === "SANITISED") counts.SANITISED++;
    else counts.ALLOWED++;
  }

  return (
    <div className="pg-distribution">
      <h3 className="pg-distribution-title pg-mono">VERDICT BREAKDOWN</h3>
      {total === 0 ? (
        <p className="pg-analytics-empty pg-mono">No prompts analyzed yet</p>
      ) : (
        <div className="pg-distribution-bars">
          {VERDICTS.map(({ key, label, color }) => {
            const count = counts[key];
            const pct = total > 0 ? Math.round((count / total) * 100) : 0;
            return (
              <div key={key} className="pg-dist-row">
                <span className="pg-dist-label pg-mono" style={{ color }}>{label}</span>
                <div className="pg-dist-track">
                  <div
                    className="pg-dist-fill"
                    style={{ width: `${pct}%`, backgroundColor: color }}
                  />
                </div>
                <span className="pg-dist-count pg-mono">{count}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default VerdictBreakdown;
