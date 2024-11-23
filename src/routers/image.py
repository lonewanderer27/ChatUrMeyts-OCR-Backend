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

router = APIRouter(prefix="/image")

@router.post("/extract_block_no_image", description="Extract the block number image of the COE PDF")
async def extract_block_no_image_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting block number image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_block_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe_instance = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe_instance.load_file()

    # resize the image
    coe_instance.resize_image()

    # Extract block number image
    block_no_image = coe_instance.get_block_no_image()

    # Convert the image to a byte stream
    img_byte_arr = BytesIO()
    block_no_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Optionally, clean up the temporary file
    os.remove(temp_file_path)

    # Return the image as a StreamingResponse
    return StreamingResponse(img_byte_arr, media_type="image/png")

@router.post("/extract_bottom_image", description="Extract the bottom image of the COE PDF")
async def extract_bottom_image_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting bottom image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_bottom_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe_instance = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe_instance.load_file()

    # resize the image
    coe_instance.resize_image()

    # Extract bottom image
    bottom_image = coe_instance.get_bottom_image()

    # Convert the image to a byte stream
    img_byte_arr = BytesIO()
    bottom_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Optionally, clean up the temporary file
    os.remove(temp_file_path)

    # Return the image as a StreamingResponse
    return StreamingResponse(img_byte_arr, media_type="image/png")

@router.post("/extract_top_image", description="Extract the top image of the COE PDF")
async def extract_top_image_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting top image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_top_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe_instance = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe_instance.load_file()

    # resize the image
    coe_instance.resize_image()

    # Extract top image
    top_image = coe_instance.get_top_image()

    # Convert the image to a byte stream
    img_byte_arr = BytesIO()
    top_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Optionally, clean up the temporary file
    os.remove(temp_file_path)

    # Return the image as a StreamingResponse
    return StreamingResponse(img_byte_arr, media_type="image/png")