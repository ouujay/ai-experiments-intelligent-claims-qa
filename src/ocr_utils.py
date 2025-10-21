"""
OCR utilities for processing images and PDFs
Handles document upload, OCR extraction, and text preprocessing
"""
import io
import os
from pathlib import Path
from typing import Union
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# Get the project root directory and poppler path
PROJECT_ROOT = Path(__file__).parent.parent
POPPLER_PATH = PROJECT_ROOT / "poppler-25.07.0" / "Library" / "bin"

# Configure Tesseract path
TESSERACT_PATH = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


def load_and_ocr(file_bytes: bytes, filename: str) -> str:
    """
    Load image or PDF and extract text using OCR

    Args:
        file_bytes: Raw file bytes
        filename: Original filename (to detect file type)

    Returns:
        Extracted OCR text
    """
    filename_lower = filename.lower()

    # Handle PDF files
    if filename_lower.endswith('.pdf'):
        return ocr_pdf(file_bytes)

    # Handle image files
    elif any(filename_lower.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']):
        return ocr_image(file_bytes)

    else:
        raise ValueError(f"Unsupported file type: {filename}. Supported: PDF, PNG, JPG, JPEG, TIFF, BMP")


def ocr_image(image_bytes: bytes) -> str:
    """
    Extract text from image using Tesseract OCR

    Args:
        image_bytes: Raw image bytes

    Returns:
        Extracted text
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Run OCR with specific configuration for better results
        custom_config = r'--oem 3 --psm 6'  # LSTM OCR Engine + Assume uniform block of text
        text = pytesseract.image_to_string(image, config=custom_config)

        return text.strip()

    except Exception as e:
        raise Exception(f"Error during image OCR: {str(e)}")


def ocr_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF by converting to images and running OCR

    Args:
        pdf_bytes: Raw PDF bytes

    Returns:
        Extracted text from all pages
    """
    try:
        # Convert PDF to images (300 DPI for better quality)
        # Use local poppler installation
        images = convert_from_bytes(
            pdf_bytes,
            dpi=300,
            poppler_path=str(POPPLER_PATH)
        )

        all_text = []
        custom_config = r'--oem 3 --psm 6'

        for i, image in enumerate(images):
            # Run OCR on each page
            text = pytesseract.image_to_string(image, config=custom_config)
            all_text.append(f"--- Page {i+1} ---\n{text}")

        return "\n\n".join(all_text).strip()

    except Exception as e:
        raise Exception(f"Error during PDF OCR: {str(e)}")


def preprocess_text(text: str) -> str:
    """
    Clean and normalize OCR text

    Args:
        text: Raw OCR text

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)
