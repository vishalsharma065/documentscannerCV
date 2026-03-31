import pytesseract
from PIL import Image
import cv2
import numpy as np

# If on Windows, set this path (adjust to your install location):
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image):
    """
    Extract text from a scanned image.
    Accepts a numpy array (OpenCV image) or a file path.
    """
    if isinstance(image, str):
        pil_image = Image.open(image)
    else:
        # Convert OpenCV BGR/grayscale to PIL
        if len(image.shape) == 2:  # grayscale
            pil_image = Image.fromarray(image)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb)

    # Config: assume a single block of text (good for documents)
    config = '--psm 6'
    text = pytesseract.image_to_string(pil_image, config=config)
    return text.strip()

def extract_text_with_boxes(image):
    """Returns text with bounding box data for each word."""
    if isinstance(image, np.ndarray):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
    else:
        pil_image = image

    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    return data