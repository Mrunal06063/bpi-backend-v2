from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.projects import router as projects_router
from app.config import CORS_ORIGINS
app = FastAPI()

# CORS (for React / Next.js)
# CORS - configured via CORS_ORIGINS env variable
cors_origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)                 
app.include_router(projects_router)

@app.get("/")
def root():
    return {"status": "Backend running"}
