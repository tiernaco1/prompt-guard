import { useState } from 'react'
import './App.css'
import DemoApp from './demo-site/DemoApp'
import Widget from './widget/Widget'
import { sendChat, generateReport, resetSession } from './services/api'

function App() {
  const [isWidgetOpen, setIsWidgetOpen] = useState(false);
  const [latestAnalysis, setLatestAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);

  const handleReset = async () => {
    await resetSession();
    setAnalysisHistory([]);
    setLatestAnalysis(null);
  };

  const ATTACK_TYPE_DISPLAY = {
    'direct_jailbreak':       'Direct Jailbreak',
    'indirect_injection':     'Indirect Injection',
    'role_hijacking':         'Role Hijacking',
    'payload_smuggling':      'Payload Smuggling',
    'context_manipulation':   'Context Manipulation',
    'information_extraction': 'Info Extraction',
    'obvious_attack':         'Obvious Attack',
  };

  const handlePromptCheck = async (prompt) => {
    try {
      const result = await sendChat(prompt);

      // Normalize action for widget feed
      let normalizedAction = result.action.toUpperCase();
      if (normalizedAction === 'BLOCK') normalizedAction = 'BLOCKED';
      if (normalizedAction === 'SANITISE') normalizedAction = 'SANITISED';

      const entry = {
        id: crypto.randomUUID(),
        prompt: prompt,
        action: normalizedAction,
        tier: result.tier === 1 ? "T1" : "T2",
        timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
        responseTime: result.tier === 1 ? `${Math.floor(Math.random() * 200 + 200)}ms` : `${(Math.random() * 1.5 + 1.5).toFixed(1)}s`,
        t1Label: result.t1_label,
        escalationReason: result.escalation_reason ?? null,
        ...(result.analysis && {
          attackType: ATTACK_TYPE_DISPLAY[result.analysis.attack_type] || result.analysis.attack_type,
          severity: result.analysis.severity,
          detail: result.analysis.explanation,
          confidence: result.analysis.confidence,
          sanitisedVersion: result.analysis.sanitised_version,
        }),
        // Tier 1 OBVIOUS_ATTACK has no deep analysis — set minimal metadata for charts
        ...(!result.analysis && normalizedAction === 'BLOCKED' && {
          attackType: 'Obvious Attack',
          severity: 'critical',
        }),
      };

      setLatestAnalysis(entry);
      setAnalysisHistory(prev => [entry, ...prev]);
      
      return result;
    } catch (error) {
      console.error('Error in prompt check:', error);
      throw error;
    }
  };

  return (
    <>
      <DemoApp 
        isWidgetOpen={isWidgetOpen} 
        onPromptCheck={handlePromptCheck}
      />
      <Widget
        isOpen={isWidgetOpen}
        setIsOpen={setIsWidgetOpen}
        latestAnalysis={latestAnalysis}
        analysisHistory={analysisHistory}
        onReset={handleReset}
        generateReport={generateReport}
      />
    </>
  )
}

export default App