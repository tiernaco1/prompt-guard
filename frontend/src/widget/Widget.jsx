import { useState, useMemo } from "react";
import WidgetHeader from "./WidgetHeader";
import Stats from "./Stats";
import Tabs from "./Tabs";
import Feed from "./Feed";
import AttackDistribution from "./AttackDistribution";
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

const Widget = ({ isOpen, setIsOpen, analysisHistory = [] }) => {
  const [activeTab, setActiveTab] = useState("LIVE FEED");

  // Calculate session statistics from analysis history
  const stats = useMemo(() => {
    if (analysisHistory.length === 0) {
      return { processed: 0, blocked: 0, detectRate: 0 };
    }

    const blocked = analysisHistory.filter(entry => entry.action === 'BLOCKED').length;
    const processed = analysisHistory.length;
    const detectRate = processed > 0 ? Math.round((blocked / processed) * 100) : 0;

    return { processed, blocked, detectRate };
  }, [analysisHistory]);

  return (
    <>
      <button
        className="pg-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle PromptGuard"
      >
        <Shield size={20} />
      </button>

      <div className={`pg-widget ${isOpen ? "pg-widget--open" : ""}`}>
        <WidgetHeader onClose={() => setIsOpen(false)} />
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
          <div className="pg-placeholder pg-mono">Analytics dashboard coming soon</div>
        )}
        {activeTab === "REPORT" && (
          <div className="pg-placeholder pg-mono">Threat report generation coming soon</div>
        )}
      </div>
    </>
  );
};

export default Widget;
