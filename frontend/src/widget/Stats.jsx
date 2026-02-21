import { sessionStats } from "./mock-data";

const StatCard = ({ value, label, colorClass }) => (
  <div className="pg-stat-card">
    <div className={`pg-stat-value pg-mono ${colorClass}`}>{value}</div>
    <div className="pg-stat-label pg-mono">{label}</div>
  </div>
);

const Stats = () => (
  <div className="pg-stats">
    <StatCard value={sessionStats.processed} label="PROCESSED" colorClass="pg-stat-value--accent" />
    <StatCard value={sessionStats.blocked} label="BLOCKED" colorClass="pg-stat-value--blocked" />
    <StatCard value={`${sessionStats.detectRate}%`} label="DETECT RATE" colorClass="pg-stat-value--passed" />
  </div>
);

export default Stats;
