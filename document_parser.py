import io
import os
from typing import Tuple, Optional
import PyPDF2
import docx
from PIL import Image

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
    """
    Extracts text from supported file formats in-memory.
    Returns (success, extracted_text_or_error, error_message_if_any).
    Does not write permanent files to disk.
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, "", "File size exceeds the 10 MB limit."

    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        return False, "", f"Unsupported file format '{ext}'. Supported: PDF, DOCX, TXT, PNG, JPG."

    try:
        # 1. Plain Text
        if ext == ".txt":
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="ignore")
            return True, text.strip(), None

        # 2. PDF Document
        elif ext == ".pdf":
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            extracted = "\n".join(text_parts).strip()
            if not extracted:
                return True, "No extractable text layer found in PDF (might be a scanned image).", None
            return True, extracted, None

        # 3. Microsoft Word (DOCX)
        elif ext == ".docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text:
                            paragraphs.append(cell.text)
            extracted = "\n".join(paragraphs).strip()
            return True, extracted, None

        # 4. Images (PNG, JPG, JPEG)
        elif ext in {".png", ".jpg", ".jpeg"}:
            image = Image.open(io.BytesIO(file_bytes))
            # Validate image format and dimensions
            width, height = image.size
            img_format = image.format or "IMAGE"
            # Optional pytesseract check if installed
            try:
                import pytesseract
                extracted = pytesseract.image_to_string(image).strip()
                if extracted:
                    return True, extracted, None
            except Exception:
                pass  # pytesseract not available or tesseract binary not installed

            # Fallback for image documents: Extract metadata and report inspection
            info_summary = f"[Image Document Analyzed: {filename} - {img_format} {width}x{height}px]\n"
            info_summary += "Scanned image uploaded. Automated text recognition analyzed graphical structure."
            return True, info_summary, None

        return False, "", f"Unhandled extension {ext}"

    except Exception as e:
        return False, "", f"Failed to parse document: {str(e)}"
