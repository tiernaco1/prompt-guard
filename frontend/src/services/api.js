// API service for PromptGuard backend
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const checkPrompt = async (prompt) => {
  console.log('🔍 Calling backend API:', API_URL);
  try {
    const response = await fetch(`${API_URL}/check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Backend response:', data);
    return data;
  } catch (error) {
    console.error('❌ Backend connection failed:', error.message);
    console.log('⚠️ Using mock response instead');
    // Return mock data if backend is unavailable
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

export default { checkPrompt };
