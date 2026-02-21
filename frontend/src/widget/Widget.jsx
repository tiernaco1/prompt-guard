import { useState } from 'react'
import './Widget.css'
import { threats, stats, attackDistribution } from './mock-data'
import WidgetHeader from './WidgetHeader'
import Stats from './Stats'
import Tabs from './Tabs'
import Feed from './Feed'
import AttackDistribution from './AttackDistribution'

function Widget() {
  const [isOpen, setIsOpen] = useState(false)

  const handleTabChange = (tab) => {
    console.log('Active tab:', tab)
  }

  return (
    <>
      {/* Floating icon button - always visible */}
      <button 
        className="widget-icon-btn" 
        onClick={() => setIsOpen(!isOpen)}
        title="PromptGuard Security"
      >
        🛡️
      </button>

      {/* Widget panel - slides in when open */}
      {isOpen && (
        <div className="widget-container">
          <div className="widget-close-header">
            <button className="close-btn" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>
          <WidgetHeader />
          <Stats stats={stats}/>
          <Tabs onTabChange={handleTabChange} />
          <Feed threats={threats} />
          <AttackDistribution attacks={attackDistribution} />
          <button className="generate-report">📊 Generate Report</button>
        </div>
      )}
    </>
  )
}

export default Widget