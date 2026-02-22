import { useState, useMemo } from "react";

const ReportTab = ({ generateReport }) => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateReport();
      setReport(data.report);
    } catch {
      setError("Failed to generate report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pg-report">
      <button className="pg-report-btn pg-mono" onClick={handleGenerate} disabled={loading}>
        {loading ? "GENERATING..." : "GENERATE REPORT"}
      </button>
      {error && <p className="pg-report-error pg-mono">{error}</p>}
      {report && <pre className="pg-report-text pg-mono">{report}</pre>}
    </div>
  );
};
import WidgetHeader from "./WidgetHeader";
import Stats from "./Stats";
import Tabs from "./Tabs";
import Feed from "./Feed";
import AttackDistribution from "./AttackDistribution";
import VerdictBreakdown from "./VerdictBreakdown";
import SeverityDistribution from "./SeverityDistribution";
import TierStats from "./TierStats";
import { Shield } from "lucide-react";
import "./widget.css";

const ThreatLevelBar = ({ stats }) => {
  // Calculate threat percentage based on blocked/processed ratio
  const threatPercentage = stats.processed > 0 
    ? Math.round((stats.blocked / stats.processed) * 100) 
    : 0;
  
  // Determine threat level and color class
  let threatLevel, threatClass;
  if (threatPercentage < 10) {
    threatLevel = "LOW";
    threatClass = "low";
  } else if (threatPercentage < 25) {
    threatLevel = "MEDIUM";
    threatClass = "medium";
  } else if (threatPercentage < 40) {
    threatLevel = "HIGH";
    threatClass = "high";
  } else {
    threatLevel = "CRITICAL";
    threatClass = "critical";
  }

  return (
    <div className="pg-threat">
      <div className="pg-threat-header pg-mono">
        <span>SESSION THREAT LEVEL</span>
        <span className={`pg-threat-level pg-threat-level--${threatClass}`}>{threatLevel}</span>
      </div>
      <div className="pg-threat-track">
        <div 
          className={`pg-threat-fill pg-threat-fill--${threatClass}`}
          style={{ width: `${threatPercentage}%` }}
        />
      </div>
    </div>
  );
};

const Widget = ({ isOpen, setIsOpen, analysisHistory = [], onReset, generateReport }) => {
  const [activeTab, setActiveTab] = useState("LIVE FEED");

  // Calculate session statistics from analysis history
  const stats = useMemo(() => {
    if (analysisHistory.length === 0) {
      return { processed: 0, blocked: 0, detectRate: 0 };
    }

    const blocked = analysisHistory.filter(entry => entry.action === 'BLOCKED' || entry.action === 'SANITISED').length;
    const processed = analysisHistory.length;
    const detectRate = processed > 0 ? Math.round((blocked / processed) * 100) : 0;

    return { processed, blocked, detectRate };
  }, [analysisHistory]);

  return (
    <>
      {!isOpen && (
        <button
          className="pg-toggle-btn"
          onClick={() => setIsOpen(true)}
          aria-label="Toggle PromptGuard"
        >
          <Shield size={20} />
        </button>
      )}

      <div className={`pg-widget ${isOpen ? "pg-widget--open" : ""}`}>
        <WidgetHeader onClose={() => setIsOpen(false)} onReset={onReset} />
        <Stats stats={stats} />
        <ThreatLevelBar stats={stats} />
        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === "LIVE FEED" && (
          analysisHistory.length > 0 ? (
            <Feed entries={analysisHistory} />
          ) : (
            <div className="pg-placeholder pg-mono">No prompts analyzed yet. Send a message to start monitoring.</div>
          )
        )}
        {activeTab === "ANALYTICS" && (
          <div className="pg-analytics">
            <VerdictBreakdown entries={analysisHistory} />
            <AttackDistribution entries={analysisHistory} />
            <SeverityDistribution entries={analysisHistory} />
            <TierStats entries={analysisHistory} />
          </div>
        )}
        {activeTab === "REPORT" && (
          <ReportTab generateReport={generateReport} />
        )}
      </div>
    </>
  );
};

export default Widget;
