const StatCard = ({ value, label, colorClass }) => (
  <div className="pg-stat-card">
    <div className={`pg-stat-value pg-mono ${colorClass}`}>{value}</div>
    <div className="pg-stat-label pg-mono">{label}</div>
  </div>
);

const Stats = ({ stats }) => (
  <div className="pg-stats">
    <StatCard value={stats.processed} label="PROCESSED" colorClass="pg-stat-value--accent" />
    <StatCard value={stats.blocked} label="BLOCKED" colorClass="pg-stat-value--blocked" />
    <StatCard value={`${stats.detectRate}%`} label="DETECT RATE" colorClass="pg-stat-value--passed" />
  </div>
);

export default Stats;
