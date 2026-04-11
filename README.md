# 🧠 NeuroAI — Jarvis-like Desktop AI Agent

> A production-ready, locally-running AI agent that understands natural language and executes real actions on your desktop — powered by **Ollama (Llama3)**, **Playwright**, **OpenCV**, and **FastAPI**.

---

## 📸 Preview

```
User: "Open Chrome and play Arijit Singh"
NeuroAI: ▶️ Playing: Arijit Singh - Tum Hi Ho (YouTube)

User: "Open camera and take photo"
NeuroAI: 📸 Photo saved: photo_20260410_025201.jpg

User: "What's the weather in London?"
NeuroAI: 🌤️ London: ⛅ +14°C
```

---

## 🏗️ How It Was Built — Full Story

### The Idea
The goal was to build a **Jarvis-like AI agent** that runs 100% locally — no cloud APIs, no subscriptions. A system that can:
- Understand natural language commands
- Break them into executable steps
- Control the OS, browser, camera, and APIs
- Show real-time execution in a modern UI

### The Architecture Decision
Instead of using LangChain (heavy, slow), we built a **custom two-layer planner**:

1. **Smart Rule-Based Parser** — handles 90% of commands instantly (0ms, no LLM needed)
2. **LLM Fallback** — sends complex/unknown commands to Ollama with a 30s hard timeout

This means the agent responds **instantly** for common commands even when RAM is low.

### The Chrome Profile Problem
Early versions used `subprocess` to open Chrome, then Playwright to control it. This caused Chrome's **profile picker** to appear and block automation. 

**Fix:** Playwright launches its own **Chromium** instance directly — bypassing the profile picker entirely. No more conflicts.

### The RAM Problem
`llama3` (8B model) needs 4.6GB RAM. Most users had only 1-2GB free.

**Fix:** 
- Switched to `llama3.2:3b` (2.3GB)
- Smart fallback handles most commands without LLM at all
- Hard 30s timeout prevents hanging

### The Python 3.14 Problem
Many packages (`pydantic-core`, `greenlet`, `openai-whisper`) had no pre-built wheels for Python 3.14 and required C++ Build Tools to compile.

**Fix:** Pinned exact versions with pre-built `cp314` wheels:
- `pydantic==2.12.5` + `pydantic-core==2.41.5`
- `playwright==1.52.0` (has cp314 wheel)
- Replaced `openai-whisper` → Google STT (no compilation)
- Used `--only-binary=:all:` during install

---

## 🧠 System Architecture

```
User Input (Text / Voice)
        │
        ▼
┌─────────────────────────────┐
│     Command Planner         │
│  1. Smart Rule Parser       │  ← instant, no LLM
│  2. Ollama LLM (fallback)   │  ← llama3.2:3b, 30s timeout
└─────────────┬───────────────┘
              │  JSON Plan
              │  {"steps": [{"action": "play_youtube", "params": {"query": "Arijit Singh"}}]}
              ▼
┌─────────────────────────────┐
│     Execution Engine        │
│  • Runs steps sequentially  │
│  • Tracks context state     │
│  • Retries on failure       │
│  • Skips if already done    │
└──────┬──────────────────────┘
       │
       ├──► OS Tools        (open/close apps, run commands, screenshot)
       ├──► Browser Tools   (Playwright Chromium — YouTube, Google, websites)
       ├──► Camera Tools    (OpenCV — webcam, photo capture)
       └──► API Tools       (weather, news, HTTP)
              │
              ▼
┌─────────────────────────────┐
│     Memory (SQLite)         │
│  • Command history          │
│  • Context state            │
│  • User preferences         │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│     React UI                │
│  • Real-time WebSocket      │
│  • Live step tracker        │
│  • Light / Dark theme       │
│  • Execution logs panel     │
└─────────────────────────────┘
```

---

## 📁 Project Structure

```
NEUROAI/
│
├── main.py                    # FastAPI server + WebSocket endpoint
├── .env                       # Configuration
├── requirements.txt           # Python dependencies
├── setup.bat                  # One-click Windows setup
├── start.bat                  # One-click launcher
│
├── config/
│   └── apps.json              # App paths per OS (Windows/Mac/Linux)
│
├── agent/
│   ├── planner.py             # NLP → JSON plan (rules + LLM fallback)
│   ├── executor.py            # Step-by-step execution engine + context
│   ├── memory.py              # SQLite: history, context, preferences
│   └── scheduler.py           # Daily task scheduler (HH:MM cron)
│
├── tools/
│   ├── system_tools.py        # OS: open/close apps, run commands, screenshot
│   ├── browser_tools.py       # Playwright: YouTube, Google, websites, forms
│   ├── camera_tools.py        # OpenCV: webcam open, photo capture
│   └── api_tools.py           # HTTP: weather (wttr.in), news (Google RSS)
│
├── mcp/
│   ├── tool_registry.py       # Central map: action name → function
│   └── server.py              # MCP protocol endpoints (/mcp/tools, /mcp/invoke)
│
├── voice/
│   ├── stt.py                 # Speech-to-Text (Google STT default, Whisper optional)
│   └── tts.py                 # Text-to-Speech (pyttsx3, ElevenLabs optional)
│
├── memory/
│   └── agent_memory.db        # SQLite database (auto-created)
│
└── ui/                        # React + Tailwind frontend
    ├── src/
    │   ├── App.jsx             # Main app shell, WebSocket, theme toggle
    │   ├── index.css           # Tailwind + custom animations
    │   └── components/
    │       ├── ChatPanel.jsx   # Chat UI, live step tracker, command guide
    │       ├── LogsPanel.jsx   # Real-time execution logs
    │       └── Sidebar.jsx     # Nav, history, tools list, scheduler
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

---

## ⚙️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.10+ / FastAPI | REST API + WebSocket server |
| LLM | Ollama + Llama3.2:3b | Natural language understanding |
| Browser | Playwright (Chromium) | Web automation, YouTube, Google |
| Camera | OpenCV | Webcam access, photo capture |
| OS | subprocess + psutil | App launch/kill, shell commands |
| Memory | SQLite | History, context, preferences |
| Voice STT | Google Speech Recognition | Voice input |
| Voice TTS | pyttsx3 | Voice output |
| Frontend | React 18 + Vite | Modern chat UI |
| Styling | Tailwind CSS | Light/dark theme |
| Realtime | WebSocket | Live step streaming |

---

## ✅ Supported Actions

| Action | What It Does | Example |
|--------|-------------|---------|
| `open_app` | Launch any desktop app | `open_app(app="vscode")` |
| `close_app` | Kill a running process | `close_app(app="spotify")` |
| `open_website` | Navigate to URL in Playwright | `open_website(url="github.com")` |
| `play_youtube` | Search YouTube + auto-play first result | `play_youtube(query="Arijit Singh")` |
| `search_google` | Google search + show top results | `search_google(query="Python tutorials")` |
| `click` | Click element by text or CSS selector | `click(target="Sign in")` |
| `type` | Type text into focused element | `type(text="hello world")` |
| `scroll` | Scroll page up/down | `scroll(direction="down", amount=3)` |
| `take_screenshot` | Capture full screen | `take_screenshot(filename="snap.png")` |
| `open_camera` | Open webcam preview window | `open_camera()` |
| `click_photo` | Capture photo from webcam | `click_photo()` |
| `get_weather` | Live weather via wttr.in | `get_weather(city="London")` |
| `get_news` | Top news headlines | `get_news(topic="technology")` |
| `run_command` | Execute shell command | `run_command(cmd="ipconfig")` |
| `send_email` | Open Gmail compose | `send_email(to="x@y.com", subject="Hi")` |
| `respond` | Return text response | `respond(message="Hello!")` |

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
# 1. Download Ollama from https://ollama.ai and install it
# 2. Open a terminal and run:
ollama pull llama3.2:3b

# Verify it works:
ollama run llama3.2:3b "say hello"
```

> **Why llama3.2:3b?** It needs only ~2.3GB RAM vs 4.6GB for llama3 8B.
> If you have 16GB+ RAM, use `llama3` for better quality.

---

### Step 2 — Clone / Open the Project

```bash
cd "c:\Users\anshy\Desktop\AI PROJECT\NEUROAI"
```

---

### Step 3 — Create Python Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### Step 4 — Install Python Dependencies

```bash
# Upgrade pip first (important for Python 3.14)
python -m pip install --upgrade pip setuptools wheel

# Install all packages (binary only — no C++ compiler needed)
pip install -r requirements.txt --only-binary=:all:

# Install Playwright browser
playwright install chromium

# Install OpenCV for camera support
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

### Step 6 — Start Everything

**Option A — Automatic (two terminals):**

Terminal 1 — Backend:
```bash
venv\Scripts\activate
python main.py
```

Terminal 2 — Frontend:
```bash
cd ui
npm run dev
```

**Option B — One-click:**
```bash
start.bat
```

---

### Step 7 — Open the UI

```
http://localhost:3000
```

---

## 🧪 Example Commands

### App Control
```
Open Chrome
Open VS Code
Open calculator
Close Spotify
Open Notepad
```

### YouTube & Music
```
Open Chrome and play Arijit Singh
Play lofi music
Play Arijit Singh songs on YouTube
Watch Python tutorial on YouTube
```

### Browser Automation
```
Search Python tutorials on Google
Go to github.com
Open youtube.com
Search AI news
Open Gmail
```

### Camera
```
Open camera
Open camera and take photo
Take a screenshot
```

### Multi-step Commands
```
Open Chrome and play Arijit Singh
Open Chrome, go to Gmail, and compose mail
Open camera and click picture
Search Python on Google and click first link
```

### APIs & Info
```
What's the weather in London?
Weather in Mumbai
Get latest tech news
Get news about AI
Run command: ipconfig
Run command: dir
```

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send message, get plan + results |
| `WS` | `/ws` | Real-time WebSocket streaming |
| `GET` | `/history` | Get command history |
| `DELETE` | `/history` | Clear history |
| `GET` | `/tools` | List all 22 available tools |
| `GET` | `/context` | Current execution state |
| `POST` | `/voice/listen` | Record + transcribe voice (5s) |
| `POST` | `/schedule` | Schedule a daily task |
| `GET` | `/schedules` | List scheduled tasks |
| `GET` | `/mcp/tools` | MCP tool discovery |
| `POST` | `/mcp/invoke` | Direct tool invocation |

---

## 🧠 How the Planner Works

### 1. Smart Rule-Based Parser (instant)
Handles ~90% of commands with zero LLM calls:

```
"Open Chrome and play Arijit Singh"
  → RE_PLAY matches → play_youtube(query="Arijit Singh")

"open camera and take photo"
  → RE_CAMERA matches → [open_camera(), click_photo()]

"weather in Mumbai"
  → RE_WEATHER matches → get_weather(city="Mumbai")

"run chome and serach youtube play song"  ← typos OK
  → APP_ALIASES: "chome" → "chrome"
  → RE_YOUTUBE + RE_PLAY → play_youtube(query="song")
```

### 2. LLM Fallback (complex commands)
For commands the rules can't handle, sends to Ollama:
- Model: `llama3.2:3b`
- Hard timeout: 30 seconds
- Context window: 1024 tokens (low RAM usage)
- Falls back to rule parser if LLM fails or RAM is low

### 3. JSON Plan Format
```json
{
  "steps": [
    {"action": "open_app",    "params": {"app": "vscode"}},
    {"action": "play_youtube","params": {"query": "Arijit Singh"}},
    {"action": "get_weather", "params": {"city": "London"}}
  ],
  "summary": "Open VS Code, play Arijit Singh, check London weather"
}
```

---

## 🔁 Execution Engine

The executor runs each step sequentially with:

- **Context tracking** — remembers `current_app`, `current_url`, `last_action`
- **Skip logic** — if app already open, skips `open_app`
- **Auto-retry** — browser actions retry once on failure
- **Real-time streaming** — each step status sent via WebSocket instantly

```
Step 1: open_app(chrome)     → running → ✅ Opened chrome
Step 2: play_youtube(Arijit) → running → ▶️ Playing: Arijit Singh - Tum Hi Ho
```

---

## 🎨 UI Features

| Feature | Description |
|---------|-------------|
| Light / Dark theme | Toggle with ☀️/🌙 button, saved to localStorage |
| Live step tracker | Shows each action running/success/error in real-time inside chat |
| Execution logs panel | Right panel with color-coded log entries |
| Context bar | Shows current app + URL in header |
| Command guide | Categorized examples with click-to-run |
| Copy button | Hover any message to copy it |
| Voice input | Click mic → speak → auto-sends |
| History tab | All past commands with timestamps |
| Tools tab | All 22 tools grouped by category |
| Schedule tab | Set daily tasks at specific times |

---

## ⚠️ Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `OpenCV not installed` | opencv-python missing | `pip install opencv-python --only-binary=:all:` |
| `Server error 500` from Ollama | Not enough free RAM | Close apps to free 2.5GB, or use `llama3.2:3b` |
| `Connection refused` on :8000 | Backend not running | Run `python main.py` |
| `Connection refused` on :3000 | Frontend not running | Run `cd ui && npm run dev` |
| Browser shows profile picker | Using system Chrome | Already fixed — Playwright uses its own Chromium |
| `pydantic-core` build fails | Python 3.14 + no C++ tools | Use `pip install --only-binary=:all:` |
| `greenlet` build fails | Same as above | Already handled in requirements.txt |
| Voice not working | sounddevice/numpy missing | `pip install sounddevice numpy --only-binary=:all:` |
| Slow responses | LLM being called for simple commands | Smart fallback handles most commands instantly |
| `playwright install` fails | Network issue | Try `playwright install chromium --with-deps` |

---

## 🔊 Voice Setup

**Default (Google STT — online, no install):**
```bash
# Works out of the box, requires internet
# Set in .env:
STT_ENGINE=google
```

**Whisper (offline, requires C++ Build Tools):**
```bash
# Only if you have Visual C++ Build Tools installed:
pip install faster-whisper
# Set in .env:
STT_ENGINE=whisper
```

---

## 🧠 Switching LLM Models

Edit `agent/planner.py` line 8:

```python
MODEL = "llama3.2:3b"   # default — needs ~2.3GB RAM
MODEL = "llama3"         # better quality — needs ~4.6GB RAM  
MODEL = "phi3"           # fastest — needs ~1.5GB RAM
MODEL = "mistral"        # good balance — needs ~3GB RAM
MODEL = "llama3:70b"     # best quality — needs 40GB+ RAM
```

Then restart the backend.

---

## 📊 Memory & Personalization

All data stored in `memory/agent_memory.db` (SQLite, auto-created):

| Table | Stores |
|-------|--------|
| `history` | Every command + plan + results |
| `context` | Current app, URL, last action |
| `preferences` | User settings |

The planner uses the last 2 commands as context for better understanding of follow-up commands.

---

## 🛠️ Adding Custom Tools

1. Add your function to `tools/system_tools.py` or a new file:
```python
def my_tool(param1: str, param2: str) -> str:
    # your logic here
    return f"✅ Done: {param1}"
```

2. Register in `mcp/tool_registry.py`:
```python
from tools.my_file import my_tool
# In _register():
"my_tool_name": my_tool,
```

3. Add to planner rules in `agent/planner.py` (optional, for instant matching):
```python
if "my keyword" in t:
    return _plan([_step("my_tool_name", param1="value")], "Summary")
```

The LLM will also learn to use it automatically from the system prompt.

---

## 📦 requirements.txt Explained

```
fastapi==0.115.12        # Web framework
uvicorn[standard]==0.34.3 # ASGI server with WebSocket
httpx==0.28.1            # Async HTTP client (Ollama calls)
pydantic==2.12.5         # Data validation (cp314 wheel)
pydantic-core==2.41.5    # Pydantic core (cp314 wheel)
playwright==1.52.0       # Browser automation (cp314 wheel)
psutil==7.0.0            # Process management
pywin32==311             # Windows API (Windows only)
pyttsx3==2.90            # Text-to-speech
sounddevice==0.5.1       # Audio recording for voice
soundfile==0.12.1        # Audio file I/O
SpeechRecognition==3.10.4 # Google STT
python-dotenv==1.1.0     # .env file loading
opencv-python            # Camera/webcam support
numpy                    # Required by sounddevice + opencv
```

> All packages use pre-built binary wheels — **no C++ compiler required**.

---

## 🏆 What Makes This Different

| Feature | NeuroAI | Typical AI Agent |
|---------|---------|-----------------|
| Runs locally | ✅ 100% offline | ❌ Cloud API |
| Instant response | ✅ Rule-based (0ms) | ❌ Always calls LLM |
| Typo tolerance | ✅ "chome" → chrome | ❌ Exact match only |
| Camera support | ✅ OpenCV | ❌ Rarely |
| YouTube auto-play | ✅ Clicks first result | ❌ Just opens URL |
| No profile picker | ✅ Own Chromium | ❌ System Chrome issues |
| Low RAM mode | ✅ Works with 1GB free | ❌ Crashes |
| Light + Dark theme | ✅ Toggle button | ❌ Dark only |
| Real-time logs | ✅ WebSocket streaming | ❌ After completion |

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Built With

- **Ollama** — local LLM inference
- **Playwright** — browser automation
- **FastAPI** — async Python web framework  
- **React + Vite** — modern frontend
- **Tailwind CSS** — utility-first styling
- **OpenCV** — computer vision / camera
- **SQLite** — embedded database
- **pyttsx3** — offline text-to-speech

---

*NeuroAI v2.0 — Built as a production-ready Jarvis-like desktop AI agent*
"# NeuroAI-Pilot" 
