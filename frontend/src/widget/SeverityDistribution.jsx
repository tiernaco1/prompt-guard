const SEVERITIES = [
  { key: "critical", label: "CRITICAL", color: "var(--pg-critical)" },
  { key: "high",     label: "HIGH",     color: "var(--pg-high)" },
  { key: "medium",   label: "MEDIUM",   color: "var(--pg-medium)" },
  { key: "low",      label: "LOW",      color: "var(--pg-low)" },
];

const SeverityDistribution = ({ entries = [] }) => {
  const threats = entries.filter((e) => e.severity);
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const entry of threats) {
    const s = entry.severity.toLowerCase();
    if (s in counts) counts[s]++;
  }

  const maxCount = Math.max(...Object.values(counts), 1);

  return (
    <div className="pg-distribution">
      <h3 className="pg-distribution-title pg-mono">SEVERITY DISTRIBUTION</h3>
      {threats.length === 0 ? (
        <p className="pg-analytics-empty pg-mono">No threats detected</p>
      ) : (
        <div className="pg-distribution-bars">
          {SEVERITIES.map(({ key, label, color }) => (
            <div key={key} className="pg-dist-row">
              <span className="pg-dist-label pg-mono" style={{ color }}>{label}</span>
              <div className="pg-dist-track">
                <div
                  className="pg-dist-fill"
                  style={{
                    width: `${(counts[key] / maxCount) * 100}%`,
                    backgroundColor: color,
                  }}
                />
              </div>
              <span className="pg-dist-count pg-mono">{counts[key]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SeverityDistribution;
