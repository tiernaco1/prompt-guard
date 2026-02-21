import { attackDistribution, sessionStats } from "./mock-data";

const maxCount = Math.max(...attackDistribution.map((a) => a.count));

const AttackDistribution = () => (
  <div className="pg-distribution">
    <h3 className="pg-distribution-title pg-mono">ATTACK DISTRIBUTION</h3>
    <div className="pg-distribution-bars">
      {attackDistribution.map((attack) => (
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

    <div className="pg-footer-inner">
      <div className="pg-tier-legend">
        <div className="pg-tier-item">
          <span className="pg-tier-dot pg-tier-dot--t1" />
          <span className="pg-tier-text pg-mono">T1 {sessionStats.t1Avg} avg</span>
        </div>
        <div className="pg-tier-item">
          <span className="pg-tier-dot pg-tier-dot--t2" />
          <span className="pg-tier-text pg-mono">T2 {sessionStats.t2Avg} avg</span>
        </div>
      </div>
      <button className="pg-report-btn pg-mono">📋 Generate Report</button>
    </div>
  </div>
);

export default AttackDistribution;
