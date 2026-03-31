import cv2
import numpy as np
import imutils
from imutils.perspective import four_point_transform

def preprocess(image):
    """Convert to grayscale, blur, then find edges."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    return edged

def find_document_contour(edged, image):
    """Find the largest 4-sided contour (the document)."""
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    doc_contour = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_contour = approx
            break

    return doc_contour

def perspective_transform(image, contour):
    """Warp the detected document to a flat, top-down view."""
    warped = four_point_transform(image, contour.reshape(4, 2))
    return warped

def enhance_image(image):
    """Apply contrast + brightness enhancement for a clean scan look."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Adaptive thresholding gives a clean black & white scan effect
    enhanced = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 10
    )
    return enhanced

def scan_document(image_path):
    """Full pipeline: load → detect → warp → enhance."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height=500)

    edged = preprocess(image)
    contour = find_document_contour(edged, image)

    if contour is None:
        print("⚠️  No document detected. Returning enhanced original.")
        return enhance_image(orig), None

    # Scale contour back to original image size
    contour = contour * ratio
    warped = perspective_transform(orig, contour)
    enhanced = enhance_image(warped)

    return enhanced, warped  # enhanced = B&W scan, warped = color version