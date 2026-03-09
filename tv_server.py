"""Standalone server for TV display - runs independently from Gradio."""

import asyncio
import uvicorn
import httpx
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import logging
import os

# Create a local broadcaster for this server
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))
from reachy_mini_conversation_app.tv_broadcaster import TVDisplayBroadcaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create a local broadcaster instance for this server
tv_broadcaster = TVDisplayBroadcaster()

IMAGES_DIR = Path(__file__).parent / "src" / "reachy_mini_conversation_app" / "profiles" / "gumball_reflection" / "generated_images"

@app.get("/gallery")
async def serve_gallery():
    """Serve the gallery HTML page."""
    gallery_path = Path(__file__).parent / "gallery.html"
    if gallery_path.exists():
        return FileResponse(gallery_path)
    return {"error": "Gallery file not found"}

@app.get("/images")
async def list_images():
    """Return a JSON list of generated images sorted by creation time (newest first)."""
    if not IMAGES_DIR.exists():
        return JSONResponse([])
    items = []
    for f in IMAGES_DIR.glob("*.png"):
        stat = f.stat()
        items.append({
            "filename": f.name,
            "url": f"/images/{f.name}",
            "created_at_unix": int(stat.st_mtime),
        })
    items.sort(key=lambda x: x["created_at_unix"], reverse=True)
    return JSONResponse(items)

@app.get("/images/{filename}")
async def serve_image(filename: str):
    """Serve an individual image file."""
    img_path = IMAGES_DIR / filename
    if img_path.exists() and img_path.suffix == ".png":
        return FileResponse(img_path, media_type="image/png")
    return JSONResponse({"error": "Image not found"}, status_code=404)

@app.get("/")
async def serve_tv_display():
    """Serve the TV display HTML file."""
    tv_display_path = Path(__file__).parent / "tv_display.html"
    if tv_display_path.exists():
        logger.info(f"Serving TV display from: {tv_display_path}")
        return FileResponse(tv_display_path)
    else:
        return {"error": "TV display file not found"}

@app.post("/broadcast")
async def broadcast_event(request: Request):
    """Receive broadcast events from main app and forward to WebSocket clients."""
    data = await request.json()
    event_type = data.get("type")
    event_data = data.get("data", {})

    logger.info(f"Broadcasting event: {event_type}")
    await tv_broadcaster.broadcast(event_type, event_data)

    return {"status": "ok"}

@app.post("/reset")
async def reset_session():
    """Trigger a hard session reset on the main app and return the display to idle."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post("http://localhost:7860/reset")
        logger.info("Reset forwarded to main app")
    except Exception as e:
        logger.warning(f"Could not reach main app for reset: {e}")

    # Always broadcast idle so the TV display clears regardless
    await tv_broadcaster.broadcast("idle", {})
    return {"status": "ok"}

@app.websocket("/tv-display")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for TV display connections."""
    await tv_broadcaster.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from TV display: {data}")
    except Exception as e:
        logger.debug(f"TV display WebSocket closed: {e}")
    finally:
        await tv_broadcaster.disconnect(websocket)

if __name__ == "__main__":
    print("=" * 60)
    print("🎪 TV Display Server Starting")
    print("=" * 60)
    print("Open in your browser: http://localhost:8001")
    print("WebSocket will connect to: ws://localhost:8001/tv-display")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
