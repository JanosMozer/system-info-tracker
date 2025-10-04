from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import yaml
import metrics

# --- Configuration ---
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

API_KEY = config.get("security", {}).get("api_key")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(
    title="SLURM & System Info Tracker",
    description="A web dashboard to monitor a SLURM cluster and system resources.",
    version="1.0.0"
)

# Add CORS middleware to allow React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

async def verify_api_key(x_api_key: str = Depends(api_key_header)):
    """Dependency to verify the API key."""
    if not API_KEY:
        # If no API key is configured, allow access.
        return
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )

# --- API Routes ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main dashboard HTML page.
    """
    poll_interval = config.get("monitoring", {}).get("poll_interval_seconds", 10)
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "poll_interval": poll_interval * 1000, # Convert to milliseconds for JS
            "api_key": API_KEY or ""
        }
    )

@app.get("/api/metrics")
async def get_metrics_data(dependencies=[Depends(verify_api_key)]):
    """
    Provides all monitored data in JSON format.
    This endpoint is protected by an API key if one is configured.
    """
    return metrics.get_all_metrics()
