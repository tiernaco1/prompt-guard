const TierStats = ({ entries = [] }) => {
  const total = entries.length;
  const t1Count = entries.filter((e) => e.tier === "T1").length;
  const t2Count = entries.filter((e) => e.tier === "T2").length;
  const t1Pct = total > 0 ? Math.round((t1Count / total) * 100) : 0;
  const t2Pct = total > 0 ? 100 - t1Pct : 0;

  return (
    <div className="pg-distribution">
      <h3 className="pg-distribution-title pg-mono">TIER ROUTING</h3>
      {total === 0 ? (
        <p className="pg-analytics-empty pg-mono">No prompts analyzed yet</p>
      ) : (
        <>
          <div className="pg-tier-split-track">
            <div
              className="pg-tier-split-t1"
              style={{ width: `${t1Pct}%` }}
              title={`Tier 1: ${t1Count} prompts`}
            />
            <div
              className="pg-tier-split-t2"
              style={{ width: `${t2Pct}%` }}
              title={`Tier 2: ${t2Count} prompts`}
            />
          </div>
          <div className="pg-tier-split-stats">
            <div className="pg-tier-split-stat">
              <span className="pg-tier-split-dot pg-tier-split-dot--t1" />
              <div>
                <div className="pg-tier-split-value pg-mono">{t1Count}</div>
                <div className="pg-tier-split-label pg-mono">T1 FAST PATH ({t1Pct}%)</div>
              </div>
            </div>
            <div className="pg-tier-split-stat">
              <span className="pg-tier-split-dot pg-tier-split-dot--t2" />
              <div>
                <div className="pg-tier-split-value pg-mono">{t2Count}</div>
                <div className="pg-tier-split-label pg-mono">T2 DEEP ANALYSIS ({t2Pct}%)</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TierStats;
