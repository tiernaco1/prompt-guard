// API service for PromptGuard demo backend
const DEMO_BACKEND_URL = import.meta.env.VITE_DEMO_BACKEND_URL || 'http://localhost:8001';

let sessionId = null;

export const sendChat = async (prompt) => {
  console.log('🔍 Calling demo backend:', DEMO_BACKEND_URL);
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (sessionId) headers['X-Session-Id'] = sessionId;

    const response = await fetch(`${DEMO_BACKEND_URL}/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`Demo backend responded with status: ${response.status}`);
    }

    const data = await response.json();

    // Persist session ID for subsequent requests
    if (data.session_id) sessionId = data.session_id;

    console.log('✅ Demo backend response:', data);
    return data;
  } catch (error) {
    console.error('❌ Demo backend connection failed:', error.message);
    console.log('⚠️ Using mock response instead');
    return getMockResponse(prompt);
  }
};

// Mock response for testing when backend is down
const getMockResponse = (prompt) => {
  const lowerPrompt = prompt.toLowerCase();
  
  // Check for suspicious patterns
  const isSuspicious = 
    lowerPrompt.includes('ignore') || 
    lowerPrompt.includes('system') || 
    lowerPrompt.includes('admin') ||
    lowerPrompt.includes('password');

  if (isSuspicious) {
    return {
      action: 'block',
      tier: 2,
      analysis: {
        verdict: 'BLOCK',
        attack_type: 'Direct Jailbreak',
        severity: 'CRITICAL',
        explanation: 'Detected potential prompt injection attempt'
      }
    };
  }

  return {
    action: 'allow',
    tier: 1
  };
};

export default { sendChat };
