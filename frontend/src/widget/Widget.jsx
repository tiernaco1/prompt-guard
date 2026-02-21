import { useState } from "react";
import WidgetHeader from "./WidgetHeader";
import Stats from "./Stats";
import Tabs from "./Tabs";
import Feed from "./Feed";
import AttackDistribution from "./AttackDistribution";
import { Shield } from "lucide-react";
import "./widget.css";

const ThreatLevelBar = () => (
  <div className="pg-threat">
    <div className="pg-threat-header pg-mono">
      <span>SESSION THREAT LEVEL</span>
      <span className="pg-threat-level">LOW</span>
    </div>
    <div className="pg-threat-track">
      <div className="pg-threat-fill" />
    </div>
  </div>
);

const Widget = () => {
  const [activeTab, setActiveTab] = useState("LIVE FEED");
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="pg-toggle-btn"
        onClick={() => setOpen(!open)}
        aria-label="Toggle PromptGuard"
      >
        <Shield size={20} />
      </button>

      <div className={`pg-widget ${open ? "pg-widget--open" : ""}`}>
        <WidgetHeader onClose={() => setOpen(false)} />
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
