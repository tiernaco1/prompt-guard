function Stats({ stats }) {
  return (
    <div className="widget-stats">
      <div className="stat">
        <div className="stat-value">{stats.processed}</div>
        <div className="stat-label">PROCESSED</div>
      </div>
      <div className="stat">
        <div className="stat-value blocked">{stats.blocked}</div>
        <div className="stat-label">BLOCKED</div>
      </div>
      <div className="stat">
        <div className="stat-value detect">{stats.detectRate}%</div>
        <div className="stat-label">DETECT RATE</div>
      </div>
    </div>
  )
}

export default Stats
