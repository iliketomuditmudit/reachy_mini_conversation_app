# TV Display for The Idea Capsule Machine

## Overview

The TV display provides a magical, full-screen visualization of the conversation happening between Reachy Mini and users. It's designed for large screens (1080p/4K TVs) in landscape orientation and features a playful "kindergarten meets candy shop" aesthetic.

## Quick Start

### 1. Start the Conversation App

Run your Reachy Mini conversation app as usual with the `--gradio` flag:

```bash
python -m reachy_mini_conversation_app --gradio
```

### 2. Open the TV Display

Open a web browser on your TV or secondary display and navigate to:

```
http://localhost:7860/tv
```

If accessing from another device on the network, replace `localhost` with your server's IP address:

```
http://192.168.1.XXX:7860/tv
```

### 3. That's It!

The TV display will automatically connect via WebSocket and show the conversation in real-time.

## Display States

The TV display has four automatic states that sync with the conversation:

### 🎪 State 1: IDLE / WELCOME
- Shows when no conversation is active
- Features: animated gumball machine, pulsing title
- Automatically displays at startup

### 💬 State 2: CONVERSATION
- Shows when user is talking with Reachy
- Features: speech bubbles (purple for Reachy, pink for user), pulsing listening visualizer
- Scrolls automatically as conversation progresses

### ✨ State 3: GENERATING
- Shows when Reachy is creating the coloring page
- Features: animated robot workers, rotating whimsical phrases, candy-stripe loading bar
- Lasts 15-30 seconds during image generation

### 🎨 State 4: REVEAL
- Shows the final generated coloring page
- Features: dramatic zoom reveal, confetti burst after 10 seconds
- Displays Print and Email buttons (stubs for future integration)

## Visual Design

- **Colors**: Deep purple/magenta backgrounds with hot pink, gold, and mint accents
- **Borders**: Candy-stripe border around entire screen
- **Background**: Floating confetti particles (circles and stars)
- **Fonts**: Fredoka One (display), Nunito (body)
- **Animation**: Smooth transitions, bouncy effects, playful movements

## Technical Details

### WebSocket Connection

The TV display connects to the backend via WebSocket at `/tv-display` endpoint. It receives real-time events:

- `idle` - Switch to welcome screen
- `conversation` - Add message to chat transcript
- `generating` - Show loading animation
- `reveal` - Display final image

### Auto-Reconnection

If the WebSocket connection drops, the display will automatically attempt to reconnect every 3 seconds.

### Dev Toolbar

A development toolbar at the bottom allows manual testing of states:

- **Idle** - Jump to welcome screen
- **Conversation** - Demo multi-message conversation
- **Generating** - Watch loading animation
- **Reveal** - Show image reveal with confetti

To hide the toolbar for production, set `PRODUCTION = true` in the HTML file (line 688).

## Customization

### Change Loading Phrases

Edit the `LOADING_PHRASES` array in `tv_display.html` (lines 697-712) to add your own whimsical phrases.

### Adjust Colors

Modify CSS variables at the top of the `<style>` section (lines 11-17):

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

Replace the Google Fonts import (line 7) and update font-family references in the CSS.

## Troubleshooting

### Display shows "WebSocket disconnected"

1. Check that the conversation app is running
2. Verify the URL matches your server address
3. Check browser console for connection errors

### Display doesn't update

1. Refresh the page to force reconnection
2. Check that the conversation app started with `--gradio` flag
3. Verify WebSocket endpoint is accessible (check firewall settings)

### Wrong display size

The display is optimized for 1080p/4K landscape TVs. For different resolutions, you may need to adjust font sizes in the CSS.

## Integration with Backend

The TV display automatically receives events from the OpenAI Realtime handler. No additional configuration is needed - just open the `/tv` endpoint and it will sync with the conversation.

### Events Broadcasted

1. **Session start** → `idle` state
2. **User speaks** → `conversation` with user message
3. **Reachy responds** → `conversation` with robot message
4. **generate_image tool called** → `generating` state
5. **Image ready** → `reveal` state with image URL

## Files

- `tv_display.html` - Main TV display interface (single HTML file)
- `src/reachy_mini_conversation_app/tv_broadcaster.py` - WebSocket broadcaster
- `src/reachy_mini_conversation_app/main.py` - WebSocket endpoint and /tv route
- `src/reachy_mini_conversation_app/openai_realtime.py` - Event broadcasting logic

## Future Enhancements

Possible additions:
- Print button integration
- Email capture and sending
- Multi-language support matching Reachy's responses
- QR code for user to scan and download their image
- Photo booth mode with countdown timer
