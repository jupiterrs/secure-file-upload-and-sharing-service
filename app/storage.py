import os
import shutil

UPLOAD_DIR = "uploads"


def save_file(file):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path


def get_file_path(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError("File not found")
    return path


def delete_file(filename):
    path = get_file_path(filename)
    os.remove(path)
