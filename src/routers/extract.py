from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Optional, List
import logging
from pprint import pprint
from ..COE import COE
from ..COETextCleaner import COETextCleaner
from io import BytesIO
from pydantic import BaseModel
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

@extract_router.post("/all", description="Extract all the information from the COE PDF", response_model=Student)
async def extract_all_info_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting all information from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    cleaner = COETextCleaner()

    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract and clean all text
    student_name = cleaner.clean_student_name(
        pytesseract.image_to_string(coe.extract_student_name())
    )
    student_no = cleaner.clean_student_no(
        pytesseract.image_to_string(coe.extract_student_no())
    )
    course_name = cleaner.clean_course(
        pytesseract.image_to_string(coe.extract_course())
    )
    block_no = cleaner.clean_block_no(
        pytesseract.image_to_string(coe.extract_block_no())
    )
    semester = cleaner.clean_semester(
        pytesseract.image_to_string(coe.extract_semester())
    )
    acad_year = cleaner.clean_acad_year(
        pytesseract.image_to_string(coe.extract_acad_year())
    )

    # extract classes
    classes_image = coe.extract_classes()
    classes = []

    # for each class, extract and clean the text
    for class_ in classes_image:
        class_code = cleaner.clean_class_code(
            pytesseract.image_to_string(class_["class_code"])
        )

        # check if class_code can be converted to an integer
        try:
            int(class_code)
        except ValueError:
            break

        subject_name = cleaner.clean_subject_name(
            pytesseract.image_to_string(class_["subject_name"])
        )
        unit_count = cleaner.clean_unit_count(
            pytesseract.image_to_string(class_["unit_count"])
        )
        schedule = cleaner.clean_schedule(
            pytesseract.image_to_string(class_["schedule"])
        )

        classes.append(Class(
            class_code=class_code,
            subject_name=subject_name,
            unit_count=unit_count,
            schedule=schedule
        ))

    # Clean up temporary file
    try:
        os.remove(temp_file_path)
    except Exception as e:
        logger.warning(f"Failed to remove temporary file: {e}")

    return Student(
        student_name=student_name,
        student_no=student_no,
        course=course_name,
        block_no=block_no,
        semester=semester,
        acad_year=acad_year,
        classes=classes
    )

@extract_router.post("/semester", description="Extract the semester from the COE PDF", response_model=Semester)
async def extract_semester_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting semester image from COE PDF")
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_semester_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_course_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_block_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_name_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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
    cleaner = TextCleaner()

    # Save the uploaded file temporarily
    temp_file_path = f"temp_acad_year_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    try:
        # init COE object
        coe = COE(temp_file_path, save_path="temp", save_images=False)
        
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