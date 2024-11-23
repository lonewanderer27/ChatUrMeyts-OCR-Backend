from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
import logging
from pprint import pprint
from ..COE import COE
from io import BytesIO
from pydantic import BaseModel
import os
import re
import pytesseract

class Class(BaseModel):
    class_code: str
    subject_name: str
    unit_count: str
    schedule: str


class Student(BaseModel):
    student_name: str
    student_no: str
    course: str
    block_no: str
    semester: str
    acad_year: str
    classes: list[Class]

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

    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # student name image
    student_name_image = coe.extract_student_name()

    # student no image
    student_no_image = coe.extract_student_no()

    # course name image
    course_name_image = coe.extract_course()

    # block no image
    block_no_image = coe.extract_block_no()

    # semester image
    semester_image = coe.extract_semester()

    # acad year image
    acad_year_image = coe.extract_acad_year()

    # for each image, extract the text
    student_name = pytesseract.image_to_string(student_name_image).replace("\n", "")
    student_no = pytesseract.image_to_string(student_no_image).replace("\n", "")
    course_name = pytesseract.image_to_string(course_name_image).replace("\n", "")
    block_no = pytesseract.image_to_string(block_no_image).replace("\n", "").capitalize()
    semester = pytesseract.image_to_string(semester_image).replace("\n", "")
    acad_year = pytesseract.image_to_string(acad_year_image).replace("\n", "")

    # print the extracted text
    print(f"Student Name: {student_name}")
    print(f"Student No: {student_no}")
    print(f"Course Name: {course_name}")
    print(f"Block No: {block_no}")
    print(f"Semester: {semester}")
    print(f"Academic Year: {acad_year}")

    # extract classes
    classes_image = coe.extract_classes()

    # classes list
    classes = []

    # for each class, extract the text
    for class_ in classes_image:
        class_code = pytesseract.image_to_string(class_["class_code"]).replace("\n", "")

        # lets check if class_code can be converted to an integer
        try:
            int(class_code)
        except ValueError:
            # this is not a class code, so we skip this class from being
            continue

        class_subject_name = pytesseract.image_to_string(class_["subject_name"]).replace("\n", "")
        class_unit_count = pytesseract.image_to_string(class_["unit_count"]).replace("\n", "")
        class_schedule = pytesseract.image_to_string(class_["schedule"]).replace("\n", "")

        classes.append(Class(
            class_code=class_code,
            subject_name=class_subject_name,
            unit_count=class_unit_count,
            schedule=class_schedule
        ))

        # print the extracted text
        print(f"Class Code: {class_code}")
        print(f"Subject Name: {class_subject_name}")
        print(f"Unit Count: {class_unit_count}")
        print(f"Schedule: {class_schedule}")

    return Student(student_name=student_name, student_no=student_no, course_name=course_name, block_no=block_no, semester=semester, acad_year=acad_year, classes=classes)

@extract_router.post("/semester", description="Extract the semester from the COE PDF")
async def extract_semester_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting semester image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_semester_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract semester image
    semester_image = coe.extract_semester()

    # Image to string
    semester = pytesseract.image_to_string(semester_image)

    # Image to string
    return {"semester": semester}

@extract_router.post("/course", description="Extract the course name from the COE PDF")
async def extract_course_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting course name image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_course_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract course name image
    course_image = coe.extract_course()

    # Image to string
    course_name = pytesseract.image_to_string(course_image)

    # using regex to extract the course name
    course_name = re.search(r"([A-Z.\s]+)", course_name).group(0)

    # Image to string
    return Course(course_name=course_name)

@extract_router.post("/block", description="Extract the block number from the COE PDF")
async def extract_block_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting block number image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_block_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract block number image
    block_no_image = coe.extract_block_no()

    # Image to string
    block_no = pytesseract.image_to_string(block_no_image)

    # Remove \n from the string
    block_no = block_no.replace("\n", "")

    # Image to string
    return BlockNo(block_no=block_no)

@extract_router.post("/student_no", description="Extract the student number from the COE PDF")
async def extract_student_no_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting student number image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_no_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract student number image
    student_no_image = coe.extract_student_no_image()

    # Image to string
    student_no = pytesseract.image_to_string(student_no_image)

    # Image to string
    return StudentNo(student_no=student_no)

@extract_router.post("/student_name", description="Extract the student name from the COE PDF")
async def extract_student_name_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting student name image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_student_name_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract student name image
    student_name_image = coe.extract_student_name()

    # Image to string
    student_name = pytesseract.image_to_string(student_name_image)

    # Image to string
    return StudentName(student_name=student_name)

@extract_router.post("/acad_year", description="Extract the academic year from the COE PDF")
async def extract_acad_year_from_pdf(coe: UploadFile = File(...)):
    logger.info("Extracting academic year image from COE PDF")

    # Save the uploaded file temporarily
    temp_file_path = f"temp_acad_year_image_{coe.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await coe.read())

    # init COE object
    coe = COE(temp_file_path, save_path="temp", save_images=False)
    
    # load the COE PDF
    coe.load_file()

    # resize the image
    coe.resize_image()

    # Extract academic year image
    acad_year_image = coe.extract_acad_year()

    # Image to string
    acad_year = pytesseract.image_to_string(acad_year_image)

    # Image to string
    return AcadYear(acad_year=acad_year)