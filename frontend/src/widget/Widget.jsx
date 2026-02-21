import { useState } from "react";
import WidgetHeader from "./WidgetHeader";
import Stats from "./Stats";
import Tabs from "./Tabs";
import Feed from "./Feed";
import AttackDistribution from "./AttackDistribution";
import { Shield } from "lucide-react";
import { sessionStats } from "./mock-data";
import "./widget.css";

const ThreatLevelBar = () => {
  // Calculate threat percentage based on blocked/processed ratio
  const threatPercentage = Math.round((sessionStats.blocked / sessionStats.processed) * 100);
  
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

const Widget = ({ isOpen, setIsOpen }) => {
  const [activeTab, setActiveTab] = useState("LIVE FEED");

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
        <Stats />
        <ThreatLevelBar />
        <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

        {activeTab === "LIVE FEED" && <Feed />}
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
