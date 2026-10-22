"""Helpers for loading an image dataset organized as base_dir/<class>/<image>."""

from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}


def load_classes(base_dir):
    """
    Return the sorted list of class names found in base_dir,
    i.e. the names of its immediate subdirectories.

    Args:
        base_dir: Path (str or Path) of the base directory.

    Returns:
        list[str]: sorted subdirectory names, suitable for load_photos().
    """
    base = Path(base_dir).absolute()
    if not base.is_dir():
        raise FileNotFoundError(f"Base directory not found: {base}")
    return sorted(
        p.name for p in base.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    )


def load_photos(base_dir, classes):
    """
    Map each class name to the list of image paths in base_dir/<class>/.

    Args:
        base_dir: Path (str or Path) of the base directory.
        classes: List of subdirectory names.

    Returns:
        dict[str, list[Path]]: class name -> sorted list of image file paths.
    """
    base = Path(base_dir).absolute()
    photos = {}
    for cls in classes:
        class_dir = base / cls
        if not class_dir.is_dir():
            raise FileNotFoundError(f"Class directory not found: {class_dir}")
        photos[cls] = sorted(
            p for p in class_dir.iterdir()
            if p.is_file() \
            and not p.name.startswith(".") \
            and p.suffix.lower() in IMAGE_EXTENSIONS
        )
    return photos


if __name__ == "__main__":
    import sys

    base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    classes = load_classes(base_dir)
    photos = load_photos(base_dir, classes)
    for cls in classes:
        print(f"{cls}: {len(photos[cls])} images")
