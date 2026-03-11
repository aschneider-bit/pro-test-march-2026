import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

# --- App ---
app = FastAPI(title="Vibe Code App")

# Static files & templates
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Serving home page")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    logger.info("Health check")
    return {"status": "ok"}
