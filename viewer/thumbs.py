import os
from pathlib import Path
from PIL import Image
import hashlib
import platform

APP_NAME = "ImageViewer"
THUMB_SIZE = (128, 128)

def get_cache_dir():
    if platform.system() == "Windows":
        base = Path(os.getenv("APPDATA"))
    else:
        base = Path.home() / ".cache"
    path = base / APP_NAME / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_thumb_path(image_path):
    # Crea un hash univoco per il path completo
    digest = hashlib.md5(image_path.encode("utf-8")).hexdigest()
    return get_cache_dir() / f"{digest}.jpg"

def generate_thumbnail(image_path):
    thumb_path = get_thumb_path(image_path)
    if not thumb_path.exists():
        try:
            with Image.open(image_path) as img:
                img.thumbnail(THUMB_SIZE)
                img.convert("RGB").save(thumb_path, "JPEG")
        except Exception as e:
            print(f"Errore creando thumbnail per {image_path}: {e}")
            return None
    return str(thumb_path)
 