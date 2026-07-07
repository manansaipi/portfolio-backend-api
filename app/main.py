from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .rate_limiter import limiter
from .routers import projects, experiences, writings, comments, certificates, upload, auth, terminal_logs
from .database import engine, Base

# Create all tables in the database automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Backend API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Hello! The Portfolio Backend API is up and running."}

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(experiences.router)
app.include_router(writings.router)
app.include_router(comments.router)
app.include_router(certificates.router)
app.include_router(upload.router)
app.include_router(terminal_logs.router)
