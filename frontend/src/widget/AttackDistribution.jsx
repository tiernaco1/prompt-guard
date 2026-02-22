const ATTACK_COLORS = {
  "Direct Jailbreak":     "hsl(0, 75%, 55%)",
  "Role Hijacking":       "hsl(230, 70%, 60%)",
  "Info Extraction":      "hsl(40, 90%, 55%)",
  "Indirect Injection":   "hsl(25, 90%, 55%)",
  "Payload Smuggling":    "hsl(270, 60%, 60%)",
  "Context Manipulation": "hsl(195, 80%, 50%)",
};

const AttackDistribution = ({ entries = [] }) => {
  const counts = {};
  for (const entry of entries) {
    if (entry.attackType) {
      counts[entry.attackType] = (counts[entry.attackType] || 0) + 1;
    }
  }

  const distribution = Object.entries(counts)
    .map(([type, count]) => ({ type, count, color: ATTACK_COLORS[type] || "var(--pg-accent)" }))
    .sort((a, b) => b.count - a.count);

  const maxCount = distribution.length > 0 ? distribution[0].count : 1;

  return (
    <div className="pg-distribution">
      <h3 className="pg-distribution-title pg-mono">ATTACK DISTRIBUTION</h3>
      {distribution.length === 0 ? (
        <p className="pg-analytics-empty pg-mono">No attacks detected</p>
      ) : (
        <div className="pg-distribution-bars">
          {distribution.map((attack) => (
            <div key={attack.type} className="pg-dist-row">
              <span className="pg-dist-label pg-mono">{attack.type}</span>
              <div className="pg-dist-track">
                <div
                  className="pg-dist-fill"
                  style={{
                    width: `${(attack.count / maxCount) * 100}%`,
                    backgroundColor: attack.color,
                  }}
                />
              </div>
              <span className="pg-dist-count pg-mono">{attack.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AttackDistribution;
