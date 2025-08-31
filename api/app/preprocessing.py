import os
from datetime import datetime
from docx import Document

def get_file_metadata(file_path: str) -> dict:
    try:
        stats = os.stat(file_path)

        return {
            "size_kb": stats.st_size / 1024,  # size in KB
            "modified_time": datetime.fromtimestamp(stats.st_mtime)
        }
    except Exception as e:
        print(f"Error getting metadata for {file_path}: {e}")
        return None, None
    
def process_folder(path: str) -> list:
    try:
        return [
            get_file_metadata(os.path.join(path, name))
            for name in os.listdir(path)
            if os.path.isfile(os.path.join(path, name)) and name.endswith('.docx')
        ]
    except Exception as e:
        print(f"Error processing folder {path}: {e}")
        return []
    
def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""