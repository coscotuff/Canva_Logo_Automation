import cv2

import numpy as np
from PIL import Image
from io import BytesIO
from cairosvg import svg2png


def resize_numpy_image(image, max_resolution=1024 * 1024):
    """
    Resizes the image to a maximum resolution of 1024x1024

    Args:
        image (np.ndarray): The image to resize
        max_resolution (int): The maximum resolution to resize to
    """
    h, w = image.shape[:2]
    k = max_resolution / (h * w)
    k = k**0.5
    h = int(np.round(h * k / 64)) * 64
    w = int(np.round(w * k / 64)) * 64
    image = cv2.resize(image, (w, h), interpolation=cv2.INTER_LANCZOS4)
    return image


def get_canny(image):
    """
    Converts the input image to a Canny Edge Image
    
    Args:
        image (Image data type): The image to convert to Canny Edge Image
    """
    if isinstance(image, str):
        canny = cv2.imread(image)
    else:
        canny = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    canny = resize_numpy_image(image=canny)
    canny = cv2.Canny(canny, 100, 200)[..., None]
    return canny


def svg_to_canny(content, save_only=False):
    """
    Converts the input SVG to a Canny Edge Image

    Args:
        content (str): The SVG content to convert to Canny Edge Image
    """
    # Convert the cleaned svg to png
    png = svg2png(bytestring=content)

    # Convert to PIL Image
    pil_img = Image.open(BytesIO(png)).convert("RGBA")

    # Convert to OpenCV Image
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)

    if save_only:
        return cv_img

    # Get the Canny Edge Image
    canny = get_canny(image=cv_img)

    return canny
