# 🧠 NeuroAI v3.0 — Jarvis-like Desktop AI Agent

> A production-ready, locally-running AI agent that understands natural language and voice commands, executes real desktop actions, shows live execution in a futuristic Iron Man Jarvis UI, and delivers real-time news across 12 fields — powered by **Ollama**, **Temporal**, **Playwright**, **OpenCV**, and **FastAPI**.

---

## 🎬 Demo

```
🎤 You speak: "Open Chrome and play Arijit Singh"

JARVIS:
  ✔ Step 1 — Open Website     → https://www.youtube.com
  ✔ Step 2 — Search YouTube   → "Arijit Singh"
  ✔ Step 3 — Play Video       → Best Of Arijit Singh 2024

🗣 Voice response: "Playing Best Of Arijit Singh 2024"
```

```
🎤 You speak: "Law news"
JARVIS: 📰 LAW NEWS:
  • Supreme Court rules on privacy case [Reuters]
  • New data protection bill passed [BBC]
  ...
```

---

## 🏗️ Architecture

```
Voice / Text Input
        │
        ▼
┌─────────────────────────────────┐
│        Command Planner          │
│  1. Smart Rule Parser (0ms)     │  ← handles 95% instantly
│  2. Ollama LLM fallback (30s)   │  ← llama3.2:3b
└──────────────┬──────────────────┘
               │  JSON Plan
               ▼
┌─────────────────────────────────┐
│     Temporal Workflow Engine    │  ← retry, timeout, state
│  • NeuroAIPlanWorkflow          │
│  • Activities (160+ actions)    │
│  • Retry policy (3 attempts)    │
│  • Falls back to Direct Exec    │
└──────┬──────────────────────────┘
       │
       ├──► Browser Tools   (Playwright Chromium)
       ├──► OS Tools        (subprocess + psutil)
       ├──► Camera Tools    (OpenCV)
       ├──► API Tools       (weather, news, crypto, stocks)
       └──► News Engine     (Google News RSS — 12 categories)
              │
              ▼
┌─────────────────────────────────┐
│     Memory (SQLite)             │
│  history · context · prefs      │
└─────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│     Iron Man Jarvis UI          │
│  React + Framer Motion          │
│  Real-time WebSocket streaming  │
│  Voice input + TTS output       │
│  Live News Panel (12 categories)│
│  Popup Notifications            │
│  Live CPU/RAM/Battery Stats     │
└─────────────────────────────────┘
```

---

## 📁 Project Structure

```
NEUROAI/
│
├── main.py                    # FastAPI server + WebSocket + news push loop
├── launch.bat                 # ONE-CLICK launcher (all services)
├── start.bat                  # Alternative launcher (separate windows)
├── temporal.exe               # Temporal CLI (bundled, Windows)
├── requirements.txt
├── .env
│
├── agent/
│   ├── planner.py             # Rule parser (95% instant) + Ollama LLM fallback
│   ├── executor.py            # Direct step executor (Temporal fallback)
│   ├── memory.py              # SQLite: history, context, preferences
│   └── scheduler.py          # Daily task scheduler (HH:MM)
│
├── temporal/
│   ├── workflow.py            # NeuroAIPlanWorkflow (sequential steps)
│   ├── activities.py          # Temporal activities wrapping all tools
│   ├── worker.py              # Temporal worker process
│   └── client.py              # Workflow trigger + stream results
│
├── tools/
│   ├── browser_tools.py       # Playwright: YouTube, Google, websites
│   ├── system_tools.py        # OS: open/close apps, screenshot, shell
│   ├── camera_tools.py        # OpenCV: webcam, photo capture (auto-close)
│   └── api_tools.py           # HTTP: weather, news, crypto, stocks, forex...
│
├── voice/
│   ├── stt.py                 # Backend STT (sounddevice + Google)
│   └── tts.py                 # Backend TTS (pyttsx3, daemon thread)
│
├── mcp/
│   ├── tool_registry.py       # Central action → function map (160+ tools)
│   └── server.py              # MCP protocol endpoints
│
├── config/
│   └── apps.json              # App paths per OS
│
├── memory/
│   └── agent_memory.db        # SQLite database (auto-created)
│
├── logs/                      # Runtime logs (auto-created)
│
└── ui/                        # React + Tailwind + Framer Motion
    └── src/
        ├── App.jsx             # Main shell, WebSocket, stats bar, news
        ├── index.css           # Jarvis theme, animations, neon effects
        └── components/
            ├── CommandInput.jsx      # Input box + TTS toggle
            ├── VoiceInput.jsx        # Real-time STT (Web Speech API)
            ├── StepTracker.jsx       # Live step execution display
            ├── LogsPanel.jsx         # Real-time execution logs
            ├── Sidebar.jsx           # History, tools, news settings, stats
            ├── NewsPanel.jsx         # Live news dashboard (12 categories)
            └── NotificationToast.jsx # Popup news notifications
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.10–3.14 / FastAPI | REST API + WebSocket server |
| LLM | Ollama + Llama3.2:3b | Natural language → JSON plan |
| Workflow | Temporal (temporalio SDK) | Reliable step execution, retry |
| Browser | Playwright (Chromium) | YouTube, Google, web automation |
| Camera | OpenCV | Webcam access, photo capture |
| OS | subprocess + psutil | App launch/kill, shell commands |
| Memory | SQLite | History, context, preferences |
| News | Google News RSS | 12 real-world category feeds |
| Voice STT | Web Speech API (browser) | Real-time voice-to-text |
| Voice STT | Google Speech Recognition | Backend fallback STT |
| Voice TTS | Browser speechSynthesis | Instant voice responses |
| Voice TTS | pyttsx3 | Backend TTS (offline) |
| Frontend | React 18 + Vite | Modern chat UI |
| Styling | Tailwind CSS | Jarvis dark theme |
| Animation | Framer Motion | Smooth UI transitions |
| Realtime | WebSocket | Live step + news streaming |

---

## ✅ Supported Actions (160+ total)

### Core Actions
| Action | Description | Example |
|--------|-------------|---------|
| `open_website` | Navigate to URL | `open_website(url="github.com")` |
| `search_youtube` | Search YouTube | `search_youtube(query="Arijit Singh")` |
| `click_first_video` | Auto-click first result | `click_first_video()` |
| `search_google` | Google search | `search_google(query="Python")` |
| `open_app` | Launch desktop app | `open_app(app="vscode")` |
| `close_app` | Kill running process | `close_app(app="spotify")` |
| `run_command` | Execute shell command | `run_command(cmd="ipconfig")` |
| `take_screenshot` | Capture full screen | `take_screenshot()` |
| `open_camera` | Open webcam preview | `open_camera()` |
| `click_photo` | Capture photo + auto-close | `click_photo()` |
| `get_weather` | Live weather | `get_weather(city="London")` |
| `get_news` | Headlines via RSS | `get_news(topic="AI")` |

### News Actions (NEW)
| Action | Description |
|--------|-------------|
| `get_news_by_category` | News for specific field (law, health, etc.) |
| `get_daily_digest` | Multi-category morning digest |
| `get_breaking_news` | Top breaking news |

### Advanced API Actions (NEW)
| Action | Description |
|--------|-------------|
| `get_crypto_price` | Bitcoin, Ethereum, etc. |
| `get_stock_price` | Live stock prices |
| `get_forex_rates` | Currency exchange rates |
| `get_earthquake_data` | Recent significant earthquakes |
| `generate_password` | Secure random password |
| `define_word` | Dictionary definition |
| `translate_text` | Translate to any language |
| `search_wikipedia` | Wikipedia summary |
| `get_github_user` | GitHub profile info |
| `get_qr_code` | Generate QR code |
| `get_joke` / `get_dad_joke` | Random jokes |
| `get_quote` | Inspirational quotes |
| `get_nasa_apod` | NASA astronomy picture |
| `get_moon_phase` | Current moon phase |
| `get_country_info` | Country details |
| `get_air_quality` | AQI for any city |

### System Actions (NEW)
| Action | Description |
|--------|-------------|
| `get_system_info` | CPU, RAM, disk, uptime |
| `get_battery` | Battery status |
| `get_wifi_info` | WiFi details |
| `ping` | Ping any host |
| `set_volume` / `mute_volume` | Volume control |
| `set_brightness` | Screen brightness |
| `lock_screen` / `sleep_pc` | Power management |
| `show_notification` | Windows toast notification |
| `set_reminder` | Timed reminder |
| `calculate` | Math expressions |
| `copy_to_clipboard` | Clipboard operations |
| `get_datetime` | Current date and time |

---

## 📰 News System (NEW)

### 12 Real-World Categories
| Category | Voice Command |
|----------|--------------|
| Technology | `"tech news"` |
| Health & Medicine | `"health news"` |
| Law & Legal | `"law news"` |
| Education | `"education news"` |
| Finance & Economy | `"finance news"` |
| Science & Research | `"science news"` |
| Sports | `"sports news"` |
| Politics | `"politics news"` |
| Business | `"business news"` |
| Entertainment | `"entertainment news"` |
| World | `"world news"` |
| India | `"india news"` |

### News Features
- **Live News Panel** — click NEWS button in header → full dashboard with 12 tabs
- **Popup Notifications** — auto-push news alerts via WebSocket
- **Configurable intervals** — 15 / 30 / 60 minutes
- **Per-category toggles** — enable/disable any category
- **Daily Digest** — `"daily digest"` → multi-category morning briefing
- **Breaking News** — `"breaking news"` → top headlines instantly

---

## 📊 Live Stats Bar (NEW)

Always visible below the header:
- **CPU %** — color coded (green → yellow → red)
- **RAM %** — with used/total MB
- **Battery** — with charging indicator
- **Network** — upload/download totals

Stats tab in sidebar with quick action buttons.

---

## 🚀 Setup Guide (Windows)

### Prerequisites

| Requirement | Version | Download |
|-------------|---------|----------|
| Python | 3.10 – 3.14 | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| Ollama | Latest | https://ollama.ai |

### Step 1 — Install Ollama & Pull Model

```bash
ollama pull llama3.2:3b
ollama run llama3.2:3b "say hello"
```

### Step 2 — Install Python Dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --only-binary=:all:
python -m playwright install chromium
pip install opencv-python --only-binary=:all:
```

### Step 3 — Install Frontend Dependencies

```bash
cd ui
npm install
cd ..
```

### Step 4 — Launch Everything

```bash
launch.bat
```

This single file:
- Kills any processes on ports 8000 / 7233 / 3000
- Starts Temporal → Worker → Backend → Frontend
- Health-checks backend before declaring ready
- Saves all logs to `logs/` folder

**Manual (4 terminals):**
```bash
temporal.exe server start-dev          # Terminal 1
python -m temporal.worker              # Terminal 2
python main.py                         # Terminal 3
cd ui && npm run dev                   # Terminal 4
```

### Step 5 — Open the UI

```
http://localhost:3000
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/status` | Temporal + Ollama status |
| `GET` | `/stats` | Live CPU / RAM / battery / network |
| `POST` | `/chat` | Send command, get plan + results |
| `WS` | `/ws` | Real-time WebSocket streaming + news push |
| `GET` | `/history` | Command history |
| `DELETE` | `/history` | Clear history |
| `GET` | `/tools` | List all 160+ tools |
| `GET` | `/context` | Current execution state |
| `POST` | `/voice/listen` | Record + transcribe (5s) |
| `POST` | `/voice/speak` | Speak text via backend TTS |
| `POST` | `/schedule` | Schedule a daily task |
| `GET` | `/schedules` | List scheduled tasks |
| `GET` | `/news/categories` | List all news categories |
| `GET` | `/news/{category}` | Articles for a category |
| `GET` | `/news/digest/all` | Multi-category digest |
| `GET` | `/news/breaking/now` | Breaking news |
| `GET` | `/notifications/settings` | Get notification config |
| `POST` | `/notifications/settings` | Update notification config |
| `POST` | `/notifications/push` | Manually push news to all clients |

---

## 🧪 Example Commands

### YouTube & Music
```
Open Chrome and play Arijit Singh
Play lofi music
Watch Python tutorial on YouTube
```

### News (All Fields)
```
Law news
Health news
Education news
Finance news
Science news
Sports news
Politics news
Breaking news
Daily digest
India news
```

### Finance & Crypto
```
Bitcoin price
Ethereum price
Stock price AAPL
USD to INR rate
Forex rates
```

### Knowledge
```
Define serendipity
Translate hello to Hindi
Wikipedia Python programming
Who is Elon Musk
```

### System
```
System info
Battery status
WiFi info
Ping google.com
Set volume 50
Lock screen
What time is it
Remind me to drink water in 30
```

### Fun
```
Tell me a joke
Dad joke
Chuck Norris joke
Give me advice
Get trivia
Generate password 20
```

### Camera
```
Open camera
Open camera and take photo     ← camera auto-closes after photo
Take a screenshot
```

### Apps & Browser
```
Open VS Code
Open calculator
Close Spotify
Search Python tutorials on Google
Go to github.com
Open Gmail
Open incognito
```

---

## 🎨 Jarvis UI Features

| Feature | Description |
|---------|-------------|
| Iron Man theme | Dark background, neon cyan/blue glow, glassmorphism |
| Floating particles | 18 animated cyan/blue/green particles |
| Cursor glow | Soft radial gradient follows mouse |
| Scan beam | Cyan line sweeps top to bottom every 6s |
| Arc reactor logo | 3 spinning rings, pulses faster when executing |
| Step cards | Slide in with spring physics, shimmer while running |
| Progress bar | Animated fill with glow effect |
| Live stats bar | CPU / RAM / Battery / Network — updates every 3s |
| NEWS button | Opens full news dashboard with 12 category tabs |
| Bell button | Toggle news popup notifications on/off |
| News toasts | Slide-in popup with auto-dismiss + progress bar |
| Stats tab | Sidebar panel with animated bars + quick actions |
| Real-time logs | Color-coded entries slide in from right |
| Voice waveform | Real mic volume visualized as animated bars |

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | Run `launch.bat` — kills old processes automatically |
| Temporal not found | `temporal.exe` is bundled — run `launch.bat` |
| Worker can't connect | Start `temporal.exe server start-dev` first |
| Browser mic denied | Click 🔒 in address bar → allow microphone |
| `OpenCV not installed` | `pip install opencv-python --only-binary=:all:` |
| Ollama error 500 | Free 2.5GB RAM or use `llama3.2:3b` |
| `pydantic-core` build fails | Use `pip install --only-binary=:all:` |
| Frontend on port 3001 | Port 3000 was busy — open `http://localhost:3001` |
| News not loading | Check internet connection — uses Google News RSS |
| venv activation fails | Use `python main.py` directly (system Python works) |

---

## 🧠 How the Planner Works

### Layer 1 — Smart Rule Parser (instant, 0ms)
Handles ~95% of commands with zero LLM calls using regex rules:

```
"law news"          → get_news_by_category(law)
"bitcoin price"     → get_crypto_price(bitcoin)
"define serendipity"→ define_word(serendipity)
"set volume 70"     → set_volume(70)
"ping google.com"   → ping(google.com)
"daily digest"      → get_daily_digest()
"generate password" → generate_password(16)
```

### Layer 2 — Ollama LLM (complex commands, 30s timeout)
- Model: `llama3.2:3b`
- Context: last 2 commands for follow-up understanding
- Falls back to rule parser if LLM fails

---

## 📊 Memory & Context

All data stored in `memory/agent_memory.db` (SQLite, auto-created):

| Table | Stores |
|-------|--------|
| `history` | Every command + plan + results |
| `context` | Current app, URL, last action |
| `preferences` | User settings |

---

## 🏆 What Makes NeuroAI v3.0 Different

| Feature | NeuroAI v3.0 | Typical AI Agent |
|---------|-------------|-----------------|
| Runs 100% locally | ✅ | ❌ Cloud API |
| Instant response | ✅ Rule-based (0ms) | ❌ Always LLM |
| 160+ tools | ✅ | ❌ 5–10 tools |
| Real-world news (12 fields) | ✅ Live RSS | ❌ None |
| News popup notifications | ✅ WebSocket push | ❌ None |
| Live system stats | ✅ CPU/RAM/Battery | ❌ None |
| Temporal workflows | ✅ Retry + state | ❌ Fire and forget |
| Real-time voice STT | ✅ Live interim text | ❌ Record then transcribe |
| Hindi + English voice | ✅ | ❌ English only |
| Iron Man Jarvis UI | ✅ Framer Motion | ❌ Basic chat |
| Typo tolerance | ✅ "chome" → chrome | ❌ Exact match |
| Camera auto-close | ✅ After photo | ❌ Manual |
| One-click launch | ✅ `launch.bat` | ❌ Multiple terminals |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Built With

- **Ollama** — local LLM inference
- **Temporal** — durable workflow execution
- **Playwright** — browser automation
- **FastAPI** — async Python web framework
- **React + Vite** — modern frontend
- **Framer Motion** — fluid animations
- **Tailwind CSS** — utility-first styling
- **OpenCV** — computer vision / camera
- **SQLite** — embedded database
- **Web Speech API** — real-time voice recognition
- **pyttsx3** — offline text-to-speech
- **Google News RSS** — live news feeds

---

*NeuroAI v3.0 — Production-ready Jarvis-like Desktop AI Agent*
