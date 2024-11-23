from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.image import router as img_router
from src.routers.extract import extract_router
import logging
import os
import uvicorn

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chaturmeytsocr = FastAPI(
    title="Chat-Ur-Meyts OCR API",
    description="API for Chat-Ur-Meyts OCR",
    version="1.0"
)

chaturmeytsocr.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:5173", "https://chat-ur-meyts.vercel.app", "https://chaturmates-v2.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"]
)

chaturmeytsocr.include_router(img_router)
chaturmeytsocr.include_router(extract_router)

@chaturmeytsocr.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(chaturmeytsocr, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))