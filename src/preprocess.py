"""Face detection, cropping and caching of preprocessed face images."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps


_CASCADE_NAME = "haarcascade_frontalface_default.xml"


def _load_cascade():
    """Load the Haar cascade, failing loudly if the XML can't be loaded."""
    candidates = []
    if hasattr(cv2, "data"):
        candidates.append(Path(cv2.data.haarcascades) / _CASCADE_NAME)
    candidates.append(Path(__file__).with_name(_CASCADE_NAME))  # local copy

    for path in candidates:
        if path.is_file():
            cascade = cv2.CascadeClassifier(str(path))
            if not cascade.empty():
                return cascade

    raise RuntimeError(
        f"Could not load {_CASCADE_NAME}. Tried: "
        + ", ".join(str(c) for c in candidates)
        + ". Download it from the OpenCV GitHub repo "
        "(data/haarcascades/) and place it next to preprocess.py."
    )


_FACE_CASCADE = _load_cascade()


"""
_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
"""


def face_preprocess(photo_path, margin=10, size=(160, 160)):
    """
    Load a photo, detect the face, crop to it with a margin, and resize.

    Pillow handles loading, cropping and resizing; OpenCV is used only
    for the face detection itself.

    Args:
        photo_path: Path (str or Path) of the image file.
        margin: Pixels of padding added around the detected face box.
        size: (width, height) of the output image.

    Returns:
        PIL.Image.Image: RGB image of the given size.

    Raises:
        FileNotFoundError: if the file doesn't exist.
        PIL.UnidentifiedImageError: if the file isn't a readable image.
        ValueError: if no face is detected.
    """
    with Image.open(photo_path) as im:
        # Respect EXIF orientation, then force 3-channel RGB.
        img = ImageOps.exif_transpose(im).convert("RGB")

    # OpenCV is used only here, on a grayscale numpy copy.
    gray = np.asarray(img.convert("L"))
    faces = _FACE_CASCADE.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    if len(faces) == 0:
        raise ValueError(f"No face detected in: {photo_path}")

    # If several faces are found, keep the largest one.
    x, y, w, h = (int(v) for v in max(faces, key=lambda f: f[2] * f[3]))

    # Add the margin, clamped to the image bounds.
    W, H = img.size
    box = (
        max(x - margin, 0),
        max(y - margin, 0),
        min(x + w + margin, W),
        min(y + h + margin, H),
    )

    return img.crop(box).resize(size, Image.LANCZOS)


def load_preprocessed(filepath):
    """
    Return the preprocessed face image for filepath, using a cached file if present.

    The cache file is hidden and sits next to the original, named with a
    leading dot and the extension replaced by ".preproc.jpg"
    (e.g. photo.png -> .photo.preproc.jpg).

    Args:
        filepath: Path (str or Path) of the original image.

    Returns:
        PIL.Image.Image: 160x160 RGB face image.
    """
    filepath = Path(filepath)
    cache_path = filepath.with_name("." + filepath.stem + ".preproc.jpg")

    if cache_path.is_file():
        try:
            with Image.open(cache_path) as im:
                return im.convert("RGB")
        except OSError:
            pass  # Cache file is unreadable/corrupt: regenerate it.

    img = face_preprocess(filepath)
    img.save(cache_path, quality=95)
    return img
