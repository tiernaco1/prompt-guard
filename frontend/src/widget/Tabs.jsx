const tabList = ["LIVE FEED", "ANALYTICS", "REPORT"];

const Tabs = ({ activeTab, onTabChange }) => (
  <div className="pg-tabs">
    {tabList.map((tab) => (
      <button
        key={tab}
        onClick={() => onTabChange(tab)}
        className={`pg-tab pg-mono${activeTab === tab ? " pg-tab--active" : ""}`}
      >
        {tab}
      </button>
    ))}
  </div>
);

export default Tabs;
