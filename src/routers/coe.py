from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import logging
from pprint import pprint
from ..COE import COE
from io import BytesIO
import os


# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

extract_router = APIRouter(prefix="/extract")

# @extract_router.post("/block", description="Extract the block number from the COE PDF")
# async def 