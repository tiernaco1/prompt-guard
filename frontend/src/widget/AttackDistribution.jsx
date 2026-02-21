function AttackDistribution({ attacks }) {
  return (
    <div className="attack-distribution">
      <div className="distribution-title">ATTACK DISTRIBUTION</div>
      {attacks.map((attack, index) => (
        <div key={index} className="distribution-item">
          <span className="attack-type">{attack.type}</span>
          <div className="distribution-bar">
            <div 
              className="bar-fill" 
              style={{ width: `${attack.percentage}%`, backgroundColor: attack.color }}
            ></div>
          </div>
          <span className="attack-count">{attack.count}</span>
        </div>
      ))}
      <div className="distribution-footer">
        <span>🟢 T1 340ms avg</span>
        <span>🔵 T2 2.1s avg</span>
      </div>
    </div>
  )
}

export default AttackDistribution
