const actionIcons = { PASSED: "✓", ALLOW: "✓", BLOCKED: "▸", BLOCK: "▸", SANITISED: "⚠", SANITIZE: "⚠" };

const FeedEntry = ({ entry }) => {
  // Normalize action to uppercase and handle different naming conventions
  const action = entry.action.toUpperCase();
  const normalizedAction = action === 'ALLOW' ? 'PASSED' : action === 'SANITIZE' ? 'SANITISED' : action;
  const key = normalizedAction.toLowerCase();

  return (
    <div className={`pg-feed-entry pg-feed-entry--${key === 'passed' ? 'passed' : key}`}>
      <div className="pg-entry-row">
        <div className="pg-entry-content">
          <div className="pg-entry-badges">
            <span className={`pg-action-badge pg-action-badge--${key === 'passed' ? 'passed' : key} pg-mono`}>
              <span>{actionIcons[action] || actionIcons[normalizedAction]}</span> {normalizedAction}
            </span>
            {entry.attackType && (
              <span className="pg-attack-type pg-mono">{entry.attackType}</span>
            )}
          </div>
          <p className="pg-entry-prompt pg-mono">{entry.prompt}</p>
          {entry.severity && (
            <div className="pg-entry-severity">
              <span className={`pg-severity-label pg-severity--${entry.severity.toLowerCase()} pg-mono`}>
                {entry.severity}
              </span>
              {entry.detail && (
                <span className="pg-entry-detail pg-mono">{entry.detail}</span>
              )}
            </div>
          )}
        </div>
        <div className="pg-entry-meta">
          <div className="pg-entry-tier-row">
            <span className={`pg-tier pg-tier--${entry.tier.toLowerCase()} pg-mono`}>
              {entry.tier}
            </span>
            <span className="pg-response-time pg-mono">{entry.responseTime}</span>
          </div>
          <div className="pg-timestamp pg-mono">{entry.timestamp}</div>
        </div>
      </div>
    </div>
  );
};

const Feed = ({ entries }) => (
  <div className="pg-feed">
    {entries.map((entry) => (
      <FeedEntry key={entry.id} entry={entry} />
    ))}
  </div>
);

export default Feed;
