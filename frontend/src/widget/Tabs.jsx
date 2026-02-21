import { useState } from 'react'

function Tabs({ tabs = ['LIVE FEED', 'ANALYTICS', 'REPORT'], onTabChange }) {
  const [activeTab, setActiveTab] = useState(0)

  const handleTabClick = (index) => {
    setActiveTab(index)
    if (onTabChange) {
      onTabChange(tabs[index])
    }
  }

  return (
    <div className="widget-tabs">
      {tabs.map((tab, index) => (
        <button
          key={index}
          className={`tab ${activeTab === index ? 'active' : ''}`}
          onClick={() => handleTabClick(index)}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}

export default Tabs
