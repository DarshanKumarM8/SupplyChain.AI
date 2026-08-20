from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Ensure the .env file is loaded if dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

from app.routers import chat

app = FastAPI(title="SupplyChainAI Minimal Chat API")

# Add CORS so the frontend can hit it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the chat router
app.include_router(chat.router, prefix="/api/chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("run_chat_server:app", host="0.0.0.0", port=8000, reload=True)
