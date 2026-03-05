from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.projects import router as projects_router

app = FastAPI()

# CORS (for React / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], #restrict origins only to frontend 
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
