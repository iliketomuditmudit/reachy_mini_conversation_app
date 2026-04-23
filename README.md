# The Idea Capsule Machine

An interactive art installation built on the [Reachy Mini](https://github.com/pollen-robotics/reachy_mini/) robot. Visitors pull a capsule from a gumball machine, read the prompt inside to Reachy, have a short guided reflective conversation, and receive a personalized AI-generated coloring page as a keepsake.

This repo is a fork of [pollen-robotics/reachy_mini_conversation_app](https://github.com/pollen-robotics/reachy_mini_conversation_app), extended with:

- **`gumball_reflection` profile** — a custom personality and conversation flow for the installation
- **`generate_image` tool** — calls Google Gemini to produce a coloring-book-style image from each visitor's reflection
- **TV display system** — a fullscreen audience-facing visualization served on a secondary display

---

## How it works

1. Visitor pulls a pink capsule from the gumball machine
2. Reachy greets them and asks them to open the capsule and read the prompt inside
3. Reachy asks up to 3 short reflective questions based on the prompt
4. After the third answer, Reachy delivers a warm closing reflection, then calls Gemini to generate a personalized coloring page
5. The TV display animates through four states — idle, conversation, generating, reveal — in real time
6. The visitor takes their coloring page to a coloring station

---

## System architecture

```
┌─────────────────────────────────────────┐
│  Main App (Port 7860)                   │
│  - Gradio voice interface               │
│  - OpenAI Realtime API                  │
│  - Reachy Mini robot control            │
│  - Broadcasts events → TV server        │
└──────────────┬──────────────────────────┘
               │ HTTP POST /broadcast
               ▼
┌─────────────────────────────────────────┐
│  TV Server (Port 8001)                  │
│  - Serves tv_display.html               │
│  - WebSocket endpoint                   │
│  - Forwards events to browser clients   │
└──────────────┬──────────────────────────┘
               │ WebSocket
               ▼
┌─────────────────────────────────────────┐
│  TV Display (Browser, secondary screen) │
│  - Four animated states                 │
│  - Real-time transcript bubbles         │
│  - Image reveal with confetti           │
└─────────────────────────────────────────┘
```

### TV display states

| State | When | What the audience sees |
|-------|------|------------------------|
| **Idle** | No active conversation | Animated gumball machine, floating confetti, pulsing title |
| **Conversation** | Visitor is talking | Real-time speech bubbles (purple = Reachy, pink = visitor) |
| **Generating** | Gemini is creating the image | Animated robot workers, rotating whimsical loading phrases |
| **Reveal** | Image is ready | Dramatic zoom-in reveal, confetti burst |

---

## Installation

### Prerequisites

- Python 3.12+
- [Reachy Mini SDK](https://github.com/pollen-robotics/reachy_mini/)
- OpenAI API key (for GPT Realtime voice)
- Google Gemini API key (for image generation)

### Setup

```bash
git clone https://github.com/iliketomuditmudit/reachy_mini_conversation_app.git
cd reachy_mini_conversation_app

uv venv --python 3.12.1
source .venv/bin/activate
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install uvicorn httpx  # required for the TV server
```

### Configure API keys

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
REACHY_MINI_CUSTOM_PROFILE=gumball_reflection
```

---

## Running the installation

You need **two terminals** running simultaneously.

### Terminal 1 — Main conversation app

```bash
source .venv/bin/activate
python -m reachy_mini_conversation_app --gradio
```

Opens the voice interface at `http://localhost:7860`.

### Terminal 2 — TV display server

```bash
source .venv/bin/activate
python tv_server.py
```

Opens the audience display at `http://localhost:8001`. Press F11 for fullscreen on the TV.

---

## Files added in this fork

| File | Purpose |
|------|---------|
| `tv_server.py` | Standalone FastAPI server for the TV display |
| `tv_display.html` | Full-screen audience visualization (single HTML file) |
| `src/.../tv_broadcaster.py` | WebSocket connection manager |
| `src/.../profiles/gumball_reflection/` | Personality, conversation flow, and `generate_image` tool |
| `TV_DISPLAY_README.md` | Operator setup guide for the TV display |

---

## Troubleshooting

**TV display shows "WebSocket disconnected"**
- Make sure `tv_server.py` is running
- Check browser console (F12) for errors
- Test manually: `curl -X POST http://localhost:8001/broadcast -H "Content-Type: application/json" -d '{"type":"idle","data":{}}'`

**Image generation fails**
- Check that `GEMINI_API_KEY` is set in `.env`
- The tool uses `gemini-3.1-flash-image-preview`

**Robot connection timeout**
- Lite (USB): run `reachy-mini-daemon` in a separate terminal first
- Wireless: start the daemon via `http://reachy-mini.local:8000`

For the full upstream troubleshooting guide, see [TV_DISPLAY_README.md](TV_DISPLAY_README.md).

---

## License

Apache 2.0 — same as the upstream repository.
