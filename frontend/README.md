# PromptGuard Frontend

A React-based security dashboard and demo application for PromptGuard - real-time prompt injection detection and prevention.

## Features

- **Security Widget**: Real-time threat monitoring with live feed, session statistics, and threat level visualization
- **Demo Application**: Sample business website with AI chat interface protected by PromptGuard
- **Backend Integration**: Connects to FastAPI backend for prompt analysis using two-tier detection system

## Tech Stack

- React 19.2.0 with Vite for fast development
- Lucide React for icons
- Custom CSS with modern design system

## Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- PromptGuard backend running on port 8000 (see `../proxy` directory)

### Installation

```bash
# Install dependencies
npm install

# Create environment file (optional)
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
VITE_API_URL=http://localhost:8000  # Backend API URL
```

If not specified, defaults to `http://localhost:8000`.

## Project Structure

```
src/
├── App.jsx                 # Root component with state management
├── services/
│   └── api.js             # Backend API integration
├── demo-site/
│   ├── DemoApp.jsx        # Sample website with AI chat
│   └── DemoApp.css        # Demo site styling
└── widget/
    ├── Widget.jsx         # Main security widget component
    ├── WidgetHeader.jsx   # Widget header with title/close
    ├── Stats.jsx          # Session statistics cards
    ├── Feed.jsx           # Live threat feed
    ├── Tabs.jsx           # Tab navigation
    ├── AttackDistribution.jsx  # Attack analytics
    ├── widget.css         # Complete widget styling
    └── mock-data.jsx      # Fallback demo data
```

## How It Works

1. **User sends message** in demo chat → Frontend calls `/check` API endpoint
2. **Backend analyzes prompt** using two-tier detection (Crusoe T1 fast classification, Claude T2 deep analysis)
3. **Frontend receives result** with action (`allow`/`block`/`sanitize`), tier, attack type, and analysis
4. **Widget updates in real-time** with threat statistics, live feed entry, and threat level bar
5. **Chat responds** based on action (normal response, blocked warning, or sanitized message)

## Backend API Integration

The frontend communicates with the PromptGuard backend via:

### `POST /check`

**Request:**

```json
{
  "prompt": "User message text"
}
```

**Response:**

```json
{
  "action": "allow" | "block" | "sanitize",
  "tier": 1 | 2,
  "analysis": {
    "verdict": "ALLOW" | "BLOCK" | "SANITIZE",
    "attack_type": "Direct Jailbreak" | "Obfuscation" | null,
    "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | null,
    "explanation": "Analysis details"
  }
}
```

## Development

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Demo Mode

If the backend is unavailable, the frontend falls back to mock responses for demonstration purposes. Mock data includes:

- Sample threat detections
- Session statistics
- Attack distribution data

## License

Built for HackEurope Hackathon
