from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional, List
import logging
from pprint import pprint
from ..COE import COE
from ..COETextCleaner import COETextCleaner
from io import BytesIO
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os
import re
import pytesseract

class Class(BaseModel):
    class_code: str
    subject_name: str
    unit_count: Optional[str] = None
    schedule: str


class Student(BaseModel):
    student_name: str
    student_no: str
    course: str
    block_no: str
    semester: str
    acad_year: str
    classes: List[Class]

class AcademicInfo(BaseModel):
    student_name: str
    student_no: str
    course: str
    block_no: str
    semester: str
    acad_year: str

class StudentName(BaseModel):
    student_name: str

class StudentNo(BaseModel):
    student_no: str

class Course(BaseModel):
    course: str

class BlockNo(BaseModel):
    block_no: str

class Semester(BaseModel):
    semester: str

class AcadYear(BaseModel):
    acad_year: str


# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

extract_router = APIRouter(prefix="/extract", tags=["Extract"])

def process_text_extraction(image, cleaner_func):
    """Helper function to process OCR and cleaning in one step"""
    text = pytesseract.image_to_string(image)
    return cleaner_func(text)

def process_class(class_images, cleaner):
    """Process a single class entry"""
    class_code = cleaner.clean_class_code(
        pytesseract.image_to_string(class_images["class_code"])
    )
    
    # Early return if invalid class code
    try:
        int(class_code)
    except ValueError:
        return None

    return Class(
        class_code=class_code,
        subject_name=cleaner.clean_subject_name(
            pytesseract.image_to_string(class_images["subject_name"])
        ),
        unit_count=cleaner.clean_unit_count(
            pytesseract.image_to_string(class_images["unit_count"])
        ),
        schedule=cleaner.clean_schedule(
            pytesseract.image_to_string(class_images["schedule"])
        )
    )

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@extract_router.post("/all", description="Extract all the information from the COE PDF", response_model=Student)
async def extract_all_info_from_pdf(coe_file: UploadFile = File(...)):
    logger.info("Extracting all information from COE PDF")

    # Read file content directly into memory
    content = await coe_file.read()
    temp_file_path = f"temp_{coe_file.filename}"
    
    try:
        # Write content to temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        # Initialize objects
        coe = COE(temp_file_path, save_images=False)
        cleaner = COETextCleaner()
        
        # Load and preprocess the PDF
        coe.load_file()
        coe.resize_image()

        # Extract all images at once
        images = {
            'student_name': coe.extract_student_name(),
            'student_no': coe.extract_student_no(),
            'course': coe.extract_course(),
            'block_no': coe.extract_block_no(),
            'semester': coe.extract_semester(),
            'acad_year': coe.extract_acad_year()
        }

        # Create mapping of cleaning functions
        cleaning_functions = {
            'student_name': cleaner.clean_student_name,
            'student_no': cleaner.clean_student_no,
            'course': cleaner.clean_course,
            'block_no': cleaner.clean_block_no,
            'semester': cleaner.clean_semester,
            'acad_year': cleaner.clean_acad_year
        }

        # Process basic information in parallel
        with ThreadPoolExecutor() as executor:
            futures = {
                key: executor.submit(process_text_extraction, img, cleaning_functions[key])
                for key, img in images.items()
            }
            
            # Get results
            results = {key: future.result() for key, future in futures.items()}

        # Process classes in parallel
        classes_image = coe.extract_classes()
        classes = []

        for batch in chunks(classes_image, 4):
            with ThreadPoolExecutor() as executor:
                batch_results = list(executor.map(
                    partial(process_class, cleaner=cleaner),
                    batch
                ))
                # Filter out None values and extend the classes list
                classes.extend([c for c in batch_results if c is not None])

        # Build the Student object with the processed classes
        return Student(
            student_name=results['student_name'],
            student_no=results['student_no'],
            course=results['course'],
            block_no=results['block_no'],
            semester=results['semester'],
            acad_year=results['acad_year'],
            classes=classes
        )

    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/academic_info", description="Extract the academic information from the COE PDF", response_model=AcademicInfo)
async def extract_all_info_from_pdf(coe_file: UploadFile = File(...)):
    logger.info("Extracting all information from COE PDF")

    # Read file content directly into memory
    content = await coe_file.read()
    temp_file_path = f"temp_{coe_file.filename}"
    
    try:
        # Write content to temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        # Initialize objects
        coe = COE(temp_file_path, save_images=False)
        cleaner = COETextCleaner()
        
        # Load and preprocess the PDF
        coe.load_file()
        coe.resize_image()

        # Extract all images at once
        images = {
            'student_name': coe.extract_student_name(),
            'student_no': coe.extract_student_no(),
            'course': coe.extract_course(),
            'block_no': coe.extract_block_no(),
            'semester': coe.extract_semester(),
            'acad_year': coe.extract_acad_year()
        }

        # Create mapping of cleaning functions
        cleaning_functions = {
            'student_name': cleaner.clean_student_name,
            'student_no': cleaner.clean_student_no,
            'course': cleaner.clean_course,
            'block_no': cleaner.clean_block_no,
            'semester': cleaner.clean_semester,
            'acad_year': cleaner.clean_acad_year
        }

        # Process basic information in parallel
        with ThreadPoolExecutor() as executor:
            futures = {
                key: executor.submit(process_text_extraction, img, cleaning_functions[key])
                for key, img in images.items()
            }
            
            # Get results
            results = {key: future.result() for key, future in futures.items()}

        # Build the Student object with the processed classes
        return AcademicInfo(
            student_name=results['student_name'],
            student_no=results['student_no'],
            course=results['course'],
            block_no=results['block_no'],
            semester=results['semester'],
            acad_year=results['acad_year'],
        )

    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/classes", description="Extract the classes from the COE PDF", response_model=List[Class])
async def extract_classes_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting classes image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_classes_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract classes
        classes_image = coe.extract_classes()

        # Process classes in parallel
        classes_image = coe.extract_classes()
        classes = []

        for batch in chunks(classes_image, 4):
            with ThreadPoolExecutor() as executor:
                batch_results = list(executor.map(
                    partial(process_class, cleaner=cleaner),
                    batch
                ))
                # Filter out None values and extend the classes list
                classes.extend([c for c in batch_results if c is not None])

        return classes

    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/semester", description="Extract the semester from the COE PDF", response_model=Semester)
async def extract_semester_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting semester image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_semester_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean semester text
        semester = cleaner.clean_semester(
            pytesseract.image_to_string(coe.extract_semester())
        )

        return Semester(semester=semester)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/course", description="Extract the course name from the COE PDF", response_model=Course)
async def extract_course_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting course name image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_course_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean course name
        course_name = cleaner.clean_course(
            pytesseract.image_to_string(coe.extract_course())
        )

        return Course(course=course_name)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/block", description="Extract the block number from the COE PDF", response_model=BlockNo)
async def extract_block_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting block number image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_block_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean block number
        block_no = cleaner.clean_block_no(
            pytesseract.image_to_string(coe.extract_block_no())
        )

        return BlockNo(block_no=block_no)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/student_no", description="Extract the student number from the COE PDF", response_model=StudentNo)
async def extract_student_no_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting student number image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean student number
        student_no = cleaner.clean_student_no(
            pytesseract.image_to_string(coe.extract_student_no())
        )

        return StudentNo(student_no=student_no)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/student_name", description="Extract the student name from the COE PDF", response_model=StudentName)
async def extract_student_name_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting student name image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_name_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean student name
        student_name = cleaner.clean_student_name(
            pytesseract.image_to_string(coe.extract_student_name())
        )

        return StudentName(student_name=student_name)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

@extract_router.post("/acad_year", description="Extract the academic year from the COE PDF", response_model=AcadYear)
async def extract_acad_year_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting academic year image from COE PDF")
    cleaner = COETextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_acad_year_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_images=False)
        
        # load the COE PDF
        coe.load_file()

        # resize the image
        coe.resize_image()

        # Extract and clean academic year
        acad_year = cleaner.clean_acad_year(
            pytesseract.image_to_string(coe.extract_acad_year())
        )

        return AcadYear(acad_year=acad_year)
    finally:
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")