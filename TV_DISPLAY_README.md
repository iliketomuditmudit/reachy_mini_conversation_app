# TV Display for The Idea Capsule Machine

A magical, full-screen visualization interface for the Reachy Mini art installation. Designed for large screens (1080p/4K TVs) with a playful "kindergarten meets candy shop" aesthetic.

---

## 🚀 Complete Setup Guide

### Prerequisites

1. **Python 3.12+** with virtual environment
2. **Reachy Mini robot** (or simulation mode)
3. **OpenAI API key** for GPT Realtime API
4. **Two displays** (recommended):
   - Display 1: Main conversation interface (operator view)
   - Display 2: TV display (audience view)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iliketomuditmudit/reachy_mini_conversation_app.git
   cd reachy_mini_conversation_app
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   pip install uvicorn httpx  # Additional dependencies for TV display
   ```

4. **Configure API keys**:

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   MODEL_NAME="gpt-realtime-1.5"
   REACHY_MINI_CUSTOM_PROFILE="gumball_reflection"
   ```

---

## ▶️ Running the System

The TV display requires **TWO separate servers** running simultaneously:

### Terminal 1: Main Conversation App

```bash
cd reachy_mini_conversation_app
source .venv/bin/activate
python -m reachy_mini_conversation_app --gradio
```

**What this does:**
- Starts the voice conversation interface on port **7860**
- Connects to Reachy Mini robot
- Handles OpenAI Realtime API communication
- Broadcasts events to the TV display server

**Access at:** `http://localhost:7860`

### Terminal 2: TV Display Server

```bash
cd reachy_mini_conversation_app
source .venv/bin/activate
python tv_server.py
```

**What this does:**
- Serves the TV display HTML on port **8001**
- Provides WebSocket endpoint for real-time updates
- Receives broadcast events from main app via HTTP

**Access at:** `http://localhost:8001`

---

## 🎬 How to Use

### For Operators (Running the Installation)

1. **Start both servers** (see above)
2. **Open main interface**: `http://localhost:7860` in a browser
3. **Open TV display**: `http://localhost:8001` on the TV/secondary display
4. **Press F11** on the TV display to go fullscreen
5. **Click the microphone button** on the main interface to start a conversation
6. **Watch the magic**: TV display updates automatically as the conversation progresses!

### For Visitors (Experiencing the Installation)

1. Approach the gumball machine
2. Pull a pink capsule ball
3. Open it and read the prompt inside to Reachy
4. Have a conversation with Reachy (guided by the robot)
5. Watch the TV display show the magical image generation process
6. Receive a personalized coloring page!

---

## 🎨 Display States

The TV automatically transitions through four states:

### State 1: IDLE / WELCOME
**When:** No active conversation
- Animated gumball machine
- Pulsing title: "The Idea Capsule Machine"
- Floating confetti particles

### State 2: CONVERSATION
**When:** User is talking with Reachy
- Real-time speech bubbles:
  - Purple bubbles = Reachy
  - Pink bubbles = User
- Pulsing listening visualizer
- Auto-scrolling transcript

### State 3: GENERATING
**When:** Reachy is creating the image (15-30 seconds)
- Animated robot workers painting/building
- Rotating whimsical phrases:
  - "Doing hard yakka..."
  - "Flabbergasting the pixels..."
  - "Consulting the imagination goblins..."
  - ...and 12 more!
- Candy-stripe loading bar
- Animated sketch paths appearing

### State 4: REVEAL
**When:** Image is ready
- Dramatic zoom-in reveal
- Confetti burst after 10 seconds
- Print and Email buttons (stubs for future)

---

## 🛠️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────┐
│  Main App (Port 7860)                   │
│  - Gradio voice interface               │
│  - OpenAI Realtime API                  │
│  - Robot control                        │
│  - Event broadcasting (HTTP → TV)       │
└──────────────┬──────────────────────────┘
               │ HTTP POST
               │ /broadcast
               ▼
┌─────────────────────────────────────────┐
│  TV Server (Port 8001)                  │
│  - Serves tv_display.html               │
│  - WebSocket endpoint                   │
│  - Broadcasts to connected clients      │
└──────────────┬──────────────────────────┘
               │ WebSocket
               ▼
┌─────────────────────────────────────────┐
│  TV Display (Browser)                   │
│  - Single HTML file                     │
│  - Real-time UI updates                 │
│  - 4 automatic states                   │
└─────────────────────────────────────────┘
```

### Event Flow

1. **User speaks** → Main app receives audio
2. **OpenAI processes** → Transcription returned
3. **Main app broadcasts** → `POST http://localhost:8001/broadcast` with event data
4. **TV server receives** → Forwards to all connected WebSocket clients
5. **TV display updates** → JavaScript handles event and changes UI state

### Files Modified

**New files:**
- `tv_display.html` - Complete TV display interface (standalone)
- `tv_server.py` - Standalone server for TV display
- `src/reachy_mini_conversation_app/tv_broadcaster.py` - WebSocket connection manager
- `src/reachy_mini_conversation_app/__main__.py` - Module entry point

**Modified files:**
- `src/reachy_mini_conversation_app/openai_realtime.py` - Added event broadcasting
- `src/reachy_mini_conversation_app/main.py` - Restored Gradio to root path

---

## 🎨 Customization

### Hide Dev Toolbar (Production Mode)

Edit `tv_display.html`, line ~690:
```javascript
const PRODUCTION = true;  // Change false to true
```

### Change Loading Phrases

Edit `tv_display.html`, lines ~697-712:
```javascript
const LOADING_PHRASES = [
    "Your custom phrase 1...",
    "Your custom phrase 2...",
    // Add more!
];
```

### Adjust Colors

Edit `tv_display.html`, lines ~11-17:
```css
:root {
    --deep-purple: #4a148c;
    --magenta: #880e4f;
    --hot-pink: #ff006e;
    --gold: #ffd60a;
    --mint: #06ffa5;
    --lavender: #b388ff;
}
```

### Change Fonts

Edit `tv_display.html`, line ~7:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont&display=swap" rel="stylesheet">
```

Then update CSS font-family references throughout.

---

## 🐛 Troubleshooting

### Both servers won't start

**Problem:** Port already in use
**Solution:**
```bash
# Check what's using the ports
lsof -i :7860
lsof -i :8001

# Kill the process if needed
kill -9 <PID>
```

### TV display shows "WebSocket disconnected"

**Checklist:**
1. ✅ Is `tv_server.py` running?
2. ✅ Did you restart it after making code changes?
3. ✅ Check browser console (F12) for detailed error messages
4. ✅ Verify URL is `http://localhost:8001` (not 7860)

**Test WebSocket manually:**
```bash
# Should return {"status":"ok"}
curl -X POST http://localhost:8001/broadcast \
  -H "Content-Type: application/json" \
  -d '{"type":"idle","data":{}}'
```

### TV display doesn't update during conversation

**Checklist:**
1. ✅ Did you restart the **main app** after installing `httpx`?
2. ✅ Are you using the voice interface at `http://localhost:7860`?
3. ✅ Did you click the microphone button and speak?
4. ✅ Check main app logs for HTTP POST errors
5. ✅ Check TV server logs for "Broadcasting event:" messages

**Main app logs should show:**
```
INFO:httpx:HTTP Request: POST http://localhost:8001/broadcast
```

**TV server logs should show:**
```
INFO:__main__:Broadcasting event: conversation
```

### No OpenAI API Key Error

Add your key to `.env`:
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

Or enter it directly in the Gradio interface textbox.

### Camera/microphone not detected

**macOS:** Grant permissions in System Preferences → Privacy → Camera/Microphone
**Linux:** Check PulseAudio/ALSA configuration
**Simulation:** Use `--robot-name simulation` flag

---

## 🌐 Network Setup (Multiple Devices)

To access from another device (e.g., TV on same network):

1. **Find your computer's IP address:**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   # Look for something like 192.168.1.100
   ```

2. **Update both URLs on the TV device:**
   - Main interface: `http://192.168.1.100:7860`
   - TV display: `http://192.168.1.100:8001`

3. **Firewall:** Ensure ports 7860 and 8001 are open

---

## 📊 Performance Tips

### For Smooth Operation

1. **Use Chrome/Edge** - Best WebSocket performance
2. **Close dev tools** on TV display in production
3. **Use wired ethernet** for stability
4. **Close other browser tabs** to free up resources

### Recommended Hardware

- **Computer:** MacBook Pro or equivalent (M1+ recommended)
- **TV:** Any TV with HDMI input and web browser
- **Network:** Stable WiFi (5GHz) or ethernet

---

## 🎯 Production Deployment

### Auto-start on Boot (macOS)

Create `~/Library/LaunchAgents/com.reachy.conversation.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.reachy.conversation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/.venv/bin/python</string>
        <string>-m</string>
        <string>reachy_mini_conversation_app</string>
        <string>--gradio</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/reachy_mini_conversation_app</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.reachy.conversation.plist`

### Kiosk Mode (TV Browser)

Chrome kiosk mode:
```bash
google-chrome --kiosk --app=http://localhost:8001
```

Auto-refresh on connection loss:
Edit `tv_display.html` and add error recovery to the WebSocket handler.

---

## 📝 License

Same as main repository.

## 🤝 Contributing

Issues and PRs welcome at: https://github.com/iliketomuditmudit/reachy_mini_conversation_app

## 🎉 Credits

- **Design**: Kindergarten meets candy shop aesthetic
- **Fonts**: Fredoka One, Nunito (Google Fonts)
- **Robot**: Reachy Mini by Pollen Robotics
- **AI**: OpenAI GPT Realtime API

---

**Questions?** Check the troubleshooting section or open an issue on GitHub!
