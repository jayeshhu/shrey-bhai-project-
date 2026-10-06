"""
MediScan AI - Document Processor
Demonstrates: file I/O, modules, functions, exception handling, multithreading,
              Pillow image processing, PyMuPDF PDF text extraction, OCR
"""
import os
import re
import io
import logging
import concurrent.futures
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# PDF Text Extraction using PyMuPDF (fitz)
# ─────────────────────────────────────────────────────────────
def extract_pdf_text(file_path: str) -> Tuple[str, str]:
    """
    Extract text from PDF file using PyMuPDF.
    Falls back to OCR if text content is insufficient.

    Demonstrates: file I/O, exception handling, branching, modules

    Args:
        file_path: Absolute path to the PDF file

    Returns:
        Tuple of (extracted_text, extraction_method)
    """
    try:
        import pymupdf as fitz  # PyMuPDF (modern import)

        doc = fitz.open(file_path)
        text_content = []
        total_chars = 0

        # Loop through pages - demonstrates loops
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            text_content.append(page_text)
            total_chars += len(page_text.strip())

        doc.close()
        combined_text = '\n'.join(text_content)

        # If very little text, likely a scanned PDF → try OCR
        if total_chars < 100:
            logger.info("PDF appears to be scanned/image-based, attempting OCR...")
            ocr_text = extract_pdf_images_with_ocr(file_path)
            if ocr_text:
                return ocr_text, 'ocr_on_pdf'
            return combined_text, 'pymupdf_low_content'

        return combined_text, 'pymupdf'

    except ImportError:
        logger.warning("PyMuPDF not available, cannot extract PDF text directly")
        # Try OCR fallback
        ocr_text = extract_pdf_images_with_ocr(file_path)
        if ocr_text:
            return ocr_text, 'ocr_fallback'
        return '', 'extraction_failed'

    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return '', 'extraction_error'


def extract_pdf_images_with_ocr(file_path: str) -> str:
    """
    Render PDF pages as images and run OCR on them.
    Demonstrates: image processing, file I/O, loops, exception handling
    """
    try:
        import pymupdf as fitz
        doc = fitz.open(file_path)
        all_text = []

        for page_num in range(min(len(doc), 10)):  # Limit to 10 pages
            page = doc.load_page(page_num)
            # Render at 2x resolution for better OCR
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_bytes = pix.tobytes("png")
            page_text = _run_ocr_on_image_bytes(img_bytes)
            if page_text:
                all_text.append(page_text)

        doc.close()
        return '\n'.join(all_text)

    except Exception as e:
        logger.error(f"PDF→OCR pipeline error: {e}")
        return ''


# ─────────────────────────────────────────────────────────────
# Image Text Extraction using OCR
# ─────────────────────────────────────────────────────────────
def extract_image_text(file_path: str) -> Tuple[str, str]:
    """
    Extract text from image files using OCR (EasyOCR or Tesseract).

    Demonstrates: Pillow, image processing, exception handling, branching

    Args:
        file_path: Path to image file

    Returns:
        Tuple of (extracted_text, extraction_method)
    """
    try:
        from PIL import Image
        import numpy as np

        # Open and preprocess image
        img = Image.open(file_path)
        img = _preprocess_image_for_ocr(img)

        # Convert to bytes for OCR
        img_bytes_io = io.BytesIO()
        img.save(img_bytes_io, format='PNG')
        img_bytes = img_bytes_io.getvalue()

        text = _run_ocr_on_image_bytes(img_bytes)
        if text:
            return text, 'easyocr'

        return '', 'ocr_no_text'

    except Exception as e:
        logger.error(f"Image text extraction error: {e}")
        return '', 'image_extraction_error'


def _preprocess_image_for_ocr(img) -> object:
    """
    Preprocess image to improve OCR accuracy.
    Demonstrates: Pillow image processing, NumPy arrays
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import numpy as np

        # Convert to RGB if needed
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Resize if too small
        width, height = img.size
        if width < 800 or height < 600:
            scale = max(800 / width, 600 / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Enhance contrast using Pillow
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)

        # Slightly sharpen
        img = img.filter(ImageFilter.SHARPEN)

        return img
    except Exception:
        return img  # Return original if preprocessing fails


def _run_ocr_on_image_bytes(img_bytes: bytes) -> str:
    """
    Run OCR on image bytes. Tries EasyOCR first, falls back to Tesseract.
    Demonstrates: exception handling, branching, modules
    """
    # Try EasyOCR
    try:
        import easyocr
        import numpy as np
        from PIL import Image

        img = Image.open(io.BytesIO(img_bytes))
        img_array = np.array(img)

        # Initialize reader (English)
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        results = reader.readtext(img_array, detail=0, paragraph=True)

        if results:
            return '\n'.join(results)

    except ImportError:
        logger.info("EasyOCR not available, trying Tesseract...")
    except Exception as e:
        logger.warning(f"EasyOCR failed: {e}")

    # Try Tesseract via pytesseract
    try:
        import pytesseract
        from PIL import Image

        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
        return text.strip()

    except ImportError:
        logger.info("pytesseract not available")
    except Exception as e:
        logger.warning(f"Tesseract OCR failed: {e}")

    return ''


# ─────────────────────────────────────────────────────────────
# Text Cleaning
# ─────────────────────────────────────────────────────────────
def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    Demonstrates: string methods, regex, loops, branching
    """
    if not text:
        return ''

    # Replace null bytes and control chars
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', text)

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Collapse excessive blank lines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix common OCR artifacts - demonstrates string replacement
    ocr_fixes = {
        '|': 'I',        # Pipe misread as I
        'l\b': '1',      # Lowercase l as 1 in numbers
        'O0': 'O',       # Zero/Oh confusion
    }

    # Trim each line
    lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        lines.append(stripped)

    cleaned = '\n'.join(lines)

    # Ensure we don't return massive whitespace
    return cleaned.strip()


# ─────────────────────────────────────────────────────────────
# Main Document Processing
# ─────────────────────────────────────────────────────────────
def process_document(file_path: str, file_extension: str) -> dict:
    """
    Main document processing function.
    Demonstrates: multithreading (concurrent.futures), functions, branching,
                  exception handling, dictionaries, file I/O

    Args:
        file_path: Path to the uploaded file
        file_extension: File extension (pdf, png, jpg, jpeg)

    Returns:
        Dictionary with extraction results
    """
    result = {
        'extracted_text': '',
        'extraction_method': 'none',
        'success': False,
        'error': None,
        'page_count': 0,
        'char_count': 0,
    }

    ext = file_extension.lower().lstrip('.')

    try:
        if ext == 'pdf':
            # Use multithreading for PDF processing
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future = executor.submit(extract_pdf_text, file_path)
                try:
                    text, method = future.result(timeout=60)
                except concurrent.futures.TimeoutError:
                    text, method = '', 'timeout'

        elif ext in ('png', 'jpg', 'jpeg'):
            text, method = extract_image_text(file_path)

        else:
            result['error'] = f"Unsupported file type: {ext}"
            return result

        # Clean the extracted text
        cleaned = clean_extracted_text(text)

        result.update({
            'extracted_text': cleaned,
            'extraction_method': method,
            'success': bool(cleaned),
            'char_count': len(cleaned),
        })

    except Exception as e:
        logger.error(f"Document processing error: {e}", exc_info=True)
        result['error'] = str(e)

    return result


def get_file_info(file_path: str) -> dict:
    """
    Get basic file information.
    Demonstrates: file I/O, os module, dictionaries
    """
    if not os.path.exists(file_path):
        return {'exists': False}

    stat = os.stat(file_path)
    return {
        'exists': True,
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'extension': os.path.splitext(file_path)[1].lower(),
    }
