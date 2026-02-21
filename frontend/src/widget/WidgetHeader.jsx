import { Shield, X } from "lucide-react";

const WidgetHeader = ({ onClose }) => (
  <div className="pg-header">
    <div className="pg-header-left">
      <Shield className="pg-header-icon" />
      <h1 className="pg-header-title">
        Prompt <span>Guard</span>
      </h1>
    </div>
    <div className="pg-header-right">
      <div className="pg-active-badge">
        <span className="pg-active-dot" />
        <span className="pg-active-label pg-mono">ACTIVE</span>
      </div>
      {onClose && (
        <button className="pg-close-btn" onClick={onClose} aria-label="Close panel">
          <X size={16} />
        </button>
      )}
    </div>
  </div>
);

export default WidgetHeader;

