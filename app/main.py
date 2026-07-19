from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limiter import limiter
from app.modules.projects import router as projects
from app.modules.experiences import router as experiences
from app.modules.writings import router as writings
from app.modules.comments import router as comments
from app.modules.certificates import router as certificates
from app.modules.upload import router as upload
from app.modules.auth import router as auth
from app.modules.terminal import terminal_logs, ai
from app.modules.users import router as users
from app.modules.favorites import router as favorites
from app.modules.guestbook import router as guestbook
from app.core.database import engine, Base

# Create all tables in the database automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Backend API")
app.add_middleware(GZipMiddleware, minimum_size=1000)
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
app.include_router(ai.router)
app.include_router(users.router)
app.include_router(favorites.router)
app.include_router(guestbook.router, prefix="/api/guestbook", tags=["Guestbook"])
