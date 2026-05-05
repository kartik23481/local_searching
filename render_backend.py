from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔥 Dynamic ngrok URL (runtime update)
SCRAPER_URL = ""


# ✅ Health check
@app.get("/")
def home():
    return {"status": "render backend running"}


# 🔥 IMPORTANT: Dynamic URL setter (NO redeploy needed)
@app.get("/set-scraper")
def set_scraper(url: str):
    global SCRAPER_URL
    SCRAPER_URL = url.rstrip("/")  # clean trailing slash
    return {
        "status": "updated",
        "scraper_url": SCRAPER_URL
    }


# 🔥 MAIN PROXY (matches your frontend exactly)
@app.get("/api/search")
def proxy_search(
    query: str = Query(..., min_length=1),
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1)
):
    if not SCRAPER_URL:
        raise HTTPException(status_code=500, detail="Scraper URL not set")

    try:
        response = requests.get(
            f"{SCRAPER_URL}/api/search",
            params={
                "query": query,
                "offset": offset,
                "limit": limit
            },
            timeout=400
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="No results found")

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Scraper timeout")

    except Exception as e:
        return []

@app.post("/api/track_user_behavior")
def proxy_track_user_behavior(data: dict):
    if not SCRAPER_URL:
        raise HTTPException(status_code=500, detail="Scraper URL not set")

    try:
        response = requests.post(
            f"{SCRAPER_URL}/api/track_user_behavior",
            json=data,
            timeout=300
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Tracking timeout")

    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }