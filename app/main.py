from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import projects, experiences, writings, comments, certificates, upload

app = FastAPI(title="Portfolio Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(projects.router)
app.include_router(experiences.router)
app.include_router(writings.router)
app.include_router(comments.router)
app.include_router(certificates.router)
app.include_router(upload.router)
