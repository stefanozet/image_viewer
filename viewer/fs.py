import os

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

def is_image_file(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS

def list_images_in_folder(folder_path):
    try:
        return sorted([
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if is_image_file(f)
        ])
    except Exception as e:
        print(f"Errore leggendo {folder_path}: {e}")
        return []
