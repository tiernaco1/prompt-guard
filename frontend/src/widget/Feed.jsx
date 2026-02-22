import { useState } from "react";

const actionIcons = { PASSED: "✓", ALLOW: "✓", BLOCKED: "▸", BLOCK: "▸", SANITISED: "⚠", SANITIZE: "⚠" };

const t1LabelMeta = {
  SAFE:           { label: "SAFE",           cls: "safe" },
  SUSPICIOUS:     { label: "SUSPICIOUS",     cls: "suspicious" },
  OBVIOUS_ATTACK: { label: "OBVIOUS ATTACK", cls: "obvious" },
};

const confidenceAbbr = { high: "HIGH CONF", medium: "MED CONF", low: "LOW CONF" };

const FeedEntry = ({ entry }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Normalize action to uppercase and handle different naming conventions
  const action = entry.action.toUpperCase();
  const normalizedAction = action === 'ALLOW' ? 'PASSED' : action === 'SANITIZE' ? 'SANITISED' : action;
  const key = normalizedAction.toLowerCase();

  const t1Meta = entry.t1Label ? t1LabelMeta[entry.t1Label.toUpperCase()] : null;

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
              {entry.confidence && (
                <span className={`pg-confidence pg-confidence--${entry.confidence.toLowerCase()} pg-mono`}>
                  {confidenceAbbr[entry.confidence.toLowerCase()] ?? entry.confidence.toUpperCase()}
                </span>
              )}
              {entry.detail && (
                <span className={`pg-entry-detail pg-mono ${isExpanded ? 'pg-entry-detail--expanded' : ''}`}>
                  {entry.detail}
                </span>
              )}
            </div>
          )}
          {entry.escalationReason === 'session_alert' && (
            <div className="pg-session-alert pg-mono">⚡ Session alert — escalated from T1</div>
          )}
          {isExpanded && entry.sanitisedVersion && (
            <div className="pg-sanitised-block">
              <div className="pg-sanitised-label pg-mono">SANITISED VERSION</div>
              <div className="pg-sanitised-text pg-mono">{entry.sanitisedVersion}</div>
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
          {t1Meta && (
            <div className={`pg-t1-label pg-t1-label--${t1Meta.cls} pg-mono`}>{t1Meta.label}</div>
          )}
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
