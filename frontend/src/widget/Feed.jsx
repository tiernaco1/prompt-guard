import { mockEntries } from "./mock-data";
import { useState } from "react";

const actionIcons = { PASSED: "✓", BLOCKED: "▸", SANITISED: "⚠" };

const FeedEntry = ({ entry }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const key = entry.action.toLowerCase();

  return (
    <div className={`pg-feed-entry pg-feed-entry--${key}`}>
      <div className="pg-entry-row">
        <div className="pg-entry-content">
          <div className="pg-entry-badges">
            <span className={`pg-action-badge pg-action-badge--${key} pg-mono`}>
              <span>{actionIcons[entry.action]}</span> {entry.action}
            </span>
            {entry.attackType && (
              <span className="pg-attack-type pg-mono">{entry.attackType}</span>
            )}
          </div>
          <p 
            className={`pg-entry-prompt pg-mono ${isExpanded ? 'pg-entry-prompt--expanded' : ''}`}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {entry.prompt}
          </p>
          {entry.severity && (
            <div className="pg-entry-severity">
              <span className={`pg-severity-label pg-severity--${entry.severity.toLowerCase()} pg-mono`}>
                {entry.severity}
              </span>
              {entry.detail && (
                <span className={`pg-entry-detail pg-mono ${isExpanded ? 'pg-entry-detail--expanded' : ''}`}>
                  {entry.detail}
                </span>
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

const Feed = () => (
  <div className="pg-feed">
    {mockEntries.map((entry) => (
      <FeedEntry key={entry.id} entry={entry} />
    ))}
  </div>
);

export default Feed;
