from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router

app = FastAPI()

# CORS (for React / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")

@app.get("/")
def root():
    return {"status": "Backend running"}
