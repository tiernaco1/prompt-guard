function Feed({ threats }) {
  return (
    <div className="live-feed">
      {threats.map(threat => (
        <div key={threat.id} className={`threat-item ${threat.status.toLowerCase()}`}>
          <div className="threat-header">
            <span className={`status-badge ${threat.status.toLowerCase()}`}>
              {threat.status === 'BLOCKED' ? '🚫' : '✓'} {threat.status}
            </span>
            {threat.type && <span className="threat-type">{threat.type}</span>}
            <span className="threat-meta">
              {threat.tier && <span className="tier">{threat.tier}</span>}
              <span className="confidence">{threat.confidence}</span>
            </span>
          </div>
          <div className="threat-message">"{threat.message}"</div>
          {threat.severity && (
            <>
              <div className={`severity ${threat.severity.toLowerCase()}`}>
                {threat.severity}
              </div>
              <div className="threat-description">{threat.description}</div>
            </>
          )}
          <div className="threat-time">{threat.time}</div>
        </div>
      ))}
    </div>
  )
}

export default Feed