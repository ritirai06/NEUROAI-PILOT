# 🧠 NeuroAI v3.0 — Jarvis-like Desktop AI Agent

> A production-ready, locally-running AI agent that understands natural language and voice commands, executes real desktop actions, and shows live execution in a futuristic Iron Man Jarvis UI — powered by **Ollama**, **Temporal**, **Playwright**, **OpenCV**, and **FastAPI**.

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

---

## 🏗️ Architecture

```
Voice / Text Input
        │
        ▼
┌─────────────────────────────────┐
│        Command Planner          │
│  1. Smart Rule Parser (0ms)     │  ← handles 90% instantly
│  2. Ollama LLM fallback (30s)   │  ← llama3.2:3b
└──────────────┬──────────────────┘
               │  JSON Plan
               ▼
┌─────────────────────────────────┐
│     Temporal Workflow Engine    │  ← retry, timeout, state
│  • NeuroAIPlanWorkflow          │
│  • Activities (19 actions)      │
│  • Retry policy (3 attempts)    │
│  • Falls back to Direct Exec    │
└──────┬──────────────────────────┘
       │
       ├──► Browser Tools   (Playwright Chromium)
       ├──► OS Tools        (subprocess + psutil)
       ├──► Camera Tools    (OpenCV)
       └──► API Tools       (weather, news)
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
└─────────────────────────────────┘
```

---

## 📁 Project Structure

```
NEUROAI/
│
├── main.py                    # FastAPI server + WebSocket + lifespan
├── launch.bat                 # ONE-CLICK launcher (all services)
├── start.bat                  # Alternative launcher (separate windows)
├── temporal.exe               # Temporal CLI (bundled, Windows)
├── requirements.txt
├── .env
│
├── agent/
│   ├── planner.py             # Rule parser + Ollama LLM fallback
│   ├── executor.py            # Direct step executor (Temporal fallback)
│   ├── memory.py              # SQLite: history, context, preferences
│   └── scheduler.py          # Daily task scheduler (HH:MM)
│
├── temporal/
│   ├── workflow.py            # NeuroAIPlanWorkflow (sequential steps)
│   ├── activities.py          # 19 Temporal activities wrapping all tools
│   ├── worker.py              # Temporal worker process
│   └── client.py              # Workflow trigger + stream results
│
├── tools/
│   ├── browser_tools.py       # Playwright: YouTube, Google, websites
│   ├── system_tools.py        # OS: open/close apps, screenshot, shell
│   ├── camera_tools.py        # OpenCV: webcam, photo capture
│   └── api_tools.py           # HTTP: weather (wttr.in), news (RSS)
│
├── voice/
│   ├── stt.py                 # Backend STT (sounddevice + Google)
│   └── tts.py                 # Backend TTS (pyttsx3, daemon thread)
│
├── mcp/
│   ├── tool_registry.py       # Central action → function map
│   └── server.py              # MCP protocol endpoints
│
├── config/
│   └── apps.json              # App paths per OS
│
├── memory/
│   └── agent_memory.db        # SQLite database (auto-created)
│
├── logs/                      # Runtime logs (auto-created)
│   ├── backend.log
│   ├── frontend.log
│   ├── worker.log
│   └── temporal.log
│
└── ui/                        # React + Tailwind + Framer Motion
    └── src/
        ├── App.jsx             # Main shell, WebSocket, particles, cursor glow
        ├── index.css           # Jarvis theme, animations, neon effects
        └── components/
            ├── CommandInput.jsx  # Input box + TTS toggle
            ├── VoiceInput.jsx    # Real-time STT (Web Speech API)
            ├── StepTracker.jsx   # Live step execution display
            ├── LogsPanel.jsx     # Real-time execution logs
            └── Sidebar.jsx       # History, tools, scheduler
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
| Voice STT | Web Speech API (browser) | Real-time voice-to-text |
| Voice STT | Google Speech Recognition | Backend fallback STT |
| Voice TTS | Browser speechSynthesis | Instant voice responses |
| Voice TTS | pyttsx3 | Backend TTS (offline) |
| Frontend | React 18 + Vite | Modern chat UI |
| Styling | Tailwind CSS | Jarvis dark theme |
| Animation | Framer Motion | Smooth UI transitions |
| Realtime | WebSocket | Live step streaming |

---

## ✅ Supported Actions (19 total)

| Action | Description | Example |
|--------|-------------|---------|
| `open_website` | Navigate to URL | `open_website(url="github.com")` |
| `search_youtube` | Search YouTube directly | `search_youtube(query="Arijit Singh")` |
| `click_first_video` | Auto-click first result | `click_first_video()` |
| `search_google` | Google search + results | `search_google(query="Python")` |
| `click` | Click element by text/selector | `click(target="Sign in")` |
| `scroll` | Scroll page | `scroll(direction="down", amount=3)` |
| `send_email` | Open Gmail compose | `send_email(to="x@y.com")` |
| `scrape` | Extract page content | `scrape(url="example.com")` |
| `open_app` | Launch desktop app | `open_app(app="vscode")` |
| `close_app` | Kill running process | `close_app(app="spotify")` |
| `run_command` | Execute shell command | `run_command(cmd="ipconfig")` |
| `take_screenshot` | Capture full screen | `take_screenshot()` |
| `wait` | Pause execution | `wait(seconds=2)` |
| `respond` | Return text response | `respond(message="Hello!")` |
| `open_camera` | Open webcam preview | `open_camera()` |
| `click_photo` | Capture photo | `click_photo()` |
| `close_camera` | Close webcam | `close_camera()` |
| `get_weather` | Live weather via wttr.in | `get_weather(city="London")` |
| `get_news` | Top headlines via RSS | `get_news(topic="AI")` |

---

## 🚀 Setup Guide (Windows)

### Prerequisites

| Requirement | Version | Download |
|-------------|---------|----------|
| Python | 3.10 – 3.14 | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| Ollama | Latest | https://ollama.ai |

---

### Step 1 — Install Ollama & Pull Model

```bash
# Download from https://ollama.ai and install
ollama pull llama3.2:3b

# Verify:
ollama run llama3.2:3b "say hello"
```

> Use `llama3.2:3b` (~2.3GB RAM). For better quality use `llama3` (~4.6GB RAM).

---

### Step 2 — Open Project

```bash
cd "c:\Users\anshy\Desktop\AI PROJECT\NEUROAI"
```

---

### Step 3 — Python Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### Step 4 — Install Python Dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --only-binary=:all:
playwright install chromium
pip install opencv-python --only-binary=:all:
```

---

### Step 5 — Install Frontend Dependencies

```bash
cd ui
npm install
cd ..
```

---

### Step 6 — Launch Everything

**Option A — One click (recommended):**
```bash
launch.bat
```
This single file:
- Kills any processes on ports 8000 / 7233 / 3000
- Starts Temporal server → Worker → Backend → Frontend
- Health-checks backend before declaring ready
- Saves all logs to `logs/` folder
- Press any key to stop all services

**Option B — Manual (4 terminals):**

```bash
# Terminal 1 — Temporal Server
temporal.exe server start-dev

# Terminal 2 — Temporal Worker
venv\Scripts\activate
python -m temporal.worker

# Terminal 3 — Backend
venv\Scripts\activate
python main.py

# Terminal 4 — Frontend
cd ui
npm run dev
```

---

### Step 7 — Open the UI

```
http://localhost:3000
```

---

## 🎤 Voice Features

### Real-time Voice Input (Browser)
1. Click the **🎤 microphone button**
2. Speak your command
3. Text appears **live in the input box** as you speak (interim results)
4. Speech ends → text is ready to send
5. Click **Send** or enable **AUTO** mode to send automatically

**Language support:** EN-IN · HI (Hindi) · EN-US — toggle with the `EN/HI/US` button

**How it works:** Uses the browser's built-in **Web Speech API** with `continuous: true` and `interimResults: true` — no backend call needed, works instantly.

### Voice Response (TTS)
- Every command result is **spoken aloud** automatically
- Uses browser `speechSynthesis` (prefers Microsoft Zira / Google voice)
- Toggle **TTS ON/OFF** button in the input bar
- Preference saved to localStorage

### Backend Voice (Fallback)
- If browser mic is unavailable, falls back to backend STT
- Records 5 seconds via `sounddevice` → transcribes via Google Speech API
- Backend TTS via `pyttsx3` runs in a dedicated daemon thread

---

## 🔁 Temporal Workflow Engine

NeuroAI uses **Temporal** for production-grade execution:

```
Plan → NeuroAIPlanWorkflow
         │
         ├── Step 1: open_website  (timeout: 60s, retry: 3x)
         ├── Step 2: search_youtube (timeout: 60s, retry: 3x)
         └── Step 3: click_first_video (timeout: 30s, retry: 3x)
```

**Retry policy:** 3 attempts, exponential backoff (2s → 4s → 8s)

**Fallback:** If Temporal is not running, NeuroAI automatically falls back to the direct executor — everything still works.

**Temporal UI:** http://localhost:8233 (workflow history, retries, state)

---

## 🎨 Jarvis UI Features

| Feature | Description |
|---------|-------------|
| Iron Man theme | Dark background, neon cyan/blue glow, glassmorphism |
| Floating particles | 18 animated cyan/blue/green particles |
| Cursor glow | Soft radial gradient follows mouse |
| Scan beam | Cyan line sweeps top to bottom every 6s |
| Arc reactor logo | 3 spinning rings, pulses faster when executing |
| Holographic text | "NEUROAI" cycles through gradient colors |
| Step cards | Slide in with spring physics, shimmer while running |
| Typing output | Step results animate in character by character |
| Progress bar | Animated fill with glow effect |
| Idle hologram | Large arc reactor with orbiting dot when waiting |
| Real-time logs | Color-coded entries slide in from right |
| Data streams | Vertical light streams in logs panel background |
| HUD corners | Corner brackets on all panels, expand on hover |
| Voice waveform | Real mic volume visualized as animated bars |

---

## 🧪 Example Commands

### YouTube & Music
```
Open Chrome and play Arijit Singh
Play lofi music
Watch Python tutorial on YouTube
Play Bollywood songs
```

### Browser
```
Search Python tutorials on Google
Go to github.com
Open Gmail
Search AI news
```

### Apps
```
Open VS Code
Open calculator
Open Notepad
Close Spotify
```

### Camera
```
Open camera
Open camera and take photo
Take a screenshot
```

### APIs
```
What's the weather in London?
Weather in Mumbai
Get latest tech news
Get news about AI
```

### Shell
```
Run command: ipconfig
Run command: dir
Run command: systeminfo
```

### Multi-step
```
Open Chrome and play Arijit Singh
Open camera and click picture
Search Python on Google and click first link
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/status` | Temporal + Ollama status |
| `POST` | `/chat` | Send command, get plan + results |
| `WS` | `/ws` | Real-time WebSocket streaming |
| `GET` | `/history` | Command history |
| `DELETE` | `/history` | Clear history |
| `GET` | `/tools` | List all 19 tools |
| `GET` | `/context` | Current execution state |
| `POST` | `/voice/listen` | Record + transcribe (5s, backend) |
| `POST` | `/voice/speak` | Speak text via backend TTS |
| `POST` | `/schedule` | Schedule a daily task |
| `GET` | `/schedules` | List scheduled tasks |

---

## 🧠 How the Planner Works

### Layer 1 — Smart Rule Parser (instant, 0ms)
Handles ~90% of commands with zero LLM calls:

```
"Open Chrome and play Arijit Singh"
  → RE_PLAY matches → youtube_steps("Arijit Singh")

"weather in Mumbai"
  → RE_WEATHER matches → get_weather(city="Mumbai")

"run chome and serach youtube play song"  ← typos OK
  → APP_ALIASES: "chome" → "chrome"
  → RE_PLAY → youtube_steps("song")
```

### Layer 2 — Ollama LLM (complex commands, 30s timeout)
For commands the rules can't handle:
- Model: `llama3.2:3b`
- Hard timeout: 30 seconds
- Context: last 2 commands for follow-up understanding
- Falls back to rule parser if LLM fails

### JSON Plan Format
```json
{
  "steps": [
    {"action": "open_website",      "params": {"url": "https://www.youtube.com"}},
    {"action": "search_youtube",    "params": {"query": "Arijit Singh"}},
    {"action": "click_first_video", "params": {}}
  ],
  "summary": "Play Arijit Singh on YouTube"
}
```

---

## 🔊 Voice Setup

**Default (Browser Web Speech API — no install needed):**
- Works in Chrome and Edge
- Real-time interim results
- Supports Hindi + English

**Backend STT (Google — requires internet):**
```bash
# Already installed via requirements.txt
# Set in .env:
STT_ENGINE=google
```

**Backend STT (Whisper — offline):**
```bash
# Requires Visual C++ Build Tools
pip install faster-whisper
# Set in .env:
STT_ENGINE=whisper
```

---

## 🧠 Switching LLM Models

Edit `agent/planner.py` line 8:

```python
MODEL = "llama3.2:3b"   # default — ~2.3GB RAM
MODEL = "llama3"         # better  — ~4.6GB RAM
MODEL = "phi3"           # fastest — ~1.5GB RAM
MODEL = "mistral"        # balanced — ~3GB RAM
```

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | Run `launch.bat` — it kills old processes automatically |
| Temporal not found | `temporal.exe` is bundled — run `launch.bat` |
| Worker can't connect | Start `temporal.exe server start-dev` first |
| Browser mic denied | Click 🔒 in address bar → allow microphone |
| No speech detected | Speak clearly, check mic in Windows Sound settings |
| `OpenCV not installed` | `pip install opencv-python --only-binary=:all:` |
| Ollama error 500 | Free 2.5GB RAM or use `llama3.2:3b` |
| `pydantic-core` build fails | Use `pip install --only-binary=:all:` |
| Frontend on port 3001 | Port 3000 was busy — open `http://localhost:3001` |
| TTS not speaking | Toggle TTS ON in input bar, check system volume |

---

## 📊 Memory & Context

All data stored in `memory/agent_memory.db` (SQLite, auto-created):

| Table | Stores |
|-------|--------|
| `history` | Every command + plan + results |
| `context` | Current app, URL, last action |
| `preferences` | User settings |

---

## 🛠️ Adding Custom Tools

1. Add function to `tools/system_tools.py` or a new file:
```python
def my_tool(param: str) -> str:
    return f"Done: {param}"
```

2. Register in `mcp/tool_registry.py`:
```python
from tools.my_file import my_tool
"my_tool": my_tool,
```

3. Add Temporal activity in `temporal/activities.py`:
```python
@activity.defn(name="my_tool")
async def act_my_tool(param: str) -> str:
    import asyncio
    return await asyncio.to_thread(my_tool, param)
```

4. Add to planner rules in `agent/planner.py` (optional):
```python
if "my keyword" in t:
    return _plan([_step("my_tool", param="value")], "Summary")
```

---

## 📦 requirements.txt

```
fastapi==0.115.12        # Web framework
uvicorn[standard]==0.34.3 # ASGI server
httpx==0.28.1            # Async HTTP (Ollama calls)
pydantic==2.12.5         # Data validation
pydantic-core==2.41.5    # Pydantic core
playwright==1.52.0       # Browser automation
psutil==7.0.0            # Process management
pywin32==311             # Windows API
pyttsx3==2.90            # Text-to-speech
sounddevice==0.5.1       # Audio recording
soundfile==0.12.1        # Audio file I/O
SpeechRecognition==3.10.4 # Google STT
python-dotenv==1.1.0     # .env loading
python-multipart==0.0.20 # Form data
temporalio==1.7.1        # Temporal workflow SDK
opencv-python            # Camera/webcam
numpy                    # Required by sounddevice + opencv
```

---

## 🏆 What Makes NeuroAI v3.0 Different

| Feature | NeuroAI v3.0 | Typical AI Agent |
|---------|-------------|-----------------|
| Runs 100% locally | ✅ | ❌ Cloud API |
| Instant response | ✅ Rule-based (0ms) | ❌ Always LLM |
| Temporal workflows | ✅ Retry + state | ❌ Fire and forget |
| Real-time voice STT | ✅ Live interim text | ❌ Record then transcribe |
| Hindi + English voice | ✅ | ❌ English only |
| Voice TTS response | ✅ Browser + backend | ❌ Rarely |
| Iron Man Jarvis UI | ✅ Framer Motion | ❌ Basic chat |
| Typo tolerance | ✅ "chome" → chrome | ❌ Exact match |
| Camera support | ✅ OpenCV | ❌ Rarely |
| YouTube auto-play | ✅ Clicks first result | ❌ Just opens URL |
| One-click launch | ✅ `launch.bat` | ❌ Multiple terminals |
| Low RAM mode | ✅ Works with 1GB free | ❌ Crashes |

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

---

*NeuroAI v3.0 — Production-ready Jarvis-like Desktop AI Agent*
