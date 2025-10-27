# app/app.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from .db import init_db, get_session, Dish
from sqlmodel import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time



app = FastAPI(title="DishRank MVP")
app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")

@app.get("/", include_in_schema=False)
def root():
    # point to the static index file
    index_path = Path(__file__).resolve().parent.parent / "static" / "index.html"
    return FileResponse(index_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimpleRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_sec: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_sec
        self.cache = {}

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/dishes":
            ip = getattr(request.client, "host", "unknown")
            now = time.time()
            reqs = [t for t in self.cache.get(ip, []) if now - t < self.window]
            if len(reqs) >= self.max_requests:
                from fastapi.responses import JSONResponse
                return JSONResponse({"detail": "Too many requests. Try again later."}, status_code=429)
            reqs.append(now)
            self.cache[ip] = reqs
        return await call_next(request)

app.add_middleware(SimpleRateLimiter, max_requests=20, window_sec=10)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health(): return {"ok": True}

@app.get("/dishes")
def list_dishes(session: Session = Depends(get_session)):
    return session.exec(select(Dish)).all()

@app.post("/dishes")
def add_dish(dish: Dish, session: Session = Depends(get_session)):
    # Basic sanity checks
    if not (1 <= dish.rating <= 5):
        raise HTTPException(400, "Rating must be 1–5")
    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish
