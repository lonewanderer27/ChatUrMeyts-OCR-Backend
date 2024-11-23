import re

class COETextCleaner:
    @staticmethod
    def clean_student_name(text: str) -> str:
        """Clean and format student name."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Convert to uppercase for consistency
        text = text.upper()
        # Remove any double spaces
        text = " ".join(text.split())
        return text

    @staticmethod
    def clean_student_no(text: str) -> str:
        """Clean and format student number."""
        # Remove newlines, spaces, and any non-alphanumeric characters
        text = text.replace("\n", "").strip()
        # Remove any double spaces
        text = " ".join(text.split())
        # You might want to add specific formatting rules for student numbers here
        return text

    @staticmethod
    def clean_course(text: str) -> str:
        """Clean and format course name."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Convert to uppercase for consistency
        text = text.upper()
        # Remove any double spaces
        text = " ".join(text.split())
        # Use regex to extract only alphabets, dots, and spaces
        clean_text = re.sub(r"[^A-Z.\s]", "", text)
        return clean_text.strip()

    @staticmethod
    def clean_block_no(text: str) -> str:
        """Clean and format block number."""
        # Remove newlines, spaces, and convert to uppercase
        text = text.replace("\n", "").replace(" ", "").upper()
        return text

    @staticmethod
    def clean_semester(text: str) -> str:
        """Clean and format semester."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Remove any double spaces
        text = " ".join(text.split())
        return text

    @staticmethod
    def clean_acad_year(text: str) -> str:
        """Clean and format academic year."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Remove any double spaces
        text = " ".join(text.split())
        return text

    @staticmethod
    def clean_class_code(text: str) -> str:
        """Clean and format class code."""
        # Remove newlines and spaces
        text = text.replace("\n", "").strip()
        return text

    @staticmethod
    def clean_subject_name(text: str) -> str:
        """Clean and format subject name."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Remove any double spaces
        text = " ".join(text.split())
        return text

    @staticmethod
    def clean_unit_count(text: str) -> str:
        """Clean and format unit count."""
        # Remove newlines and spaces
        text = text.replace("\n", "").strip()
        return text

    @staticmethod
    def clean_schedule(text: str) -> str:
        """Clean and format schedule."""
        # Remove newlines and extra spaces
        text = text.replace("\n", "").strip()
        # Remove any double spaces
        text = " ".join(text.split())
        return text
