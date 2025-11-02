from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, sweets

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sweet Shop Management API",
    description="A RESTful API for managing a sweet shop",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sweets.router, prefix="/api/sweets", tags=["sweets"])

@app.get("/")
def read_root():
    return {"message": "Sweet Shop Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

