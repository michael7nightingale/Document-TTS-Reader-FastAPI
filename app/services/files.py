import os.path
from uuid import uuid4


def get_name_and_extension(filename: str):
    if "." in filename:
        return filename.split('.')
    return filename, None


def path_to_static_url(filepath: str):
    static_idx = None
    dirs = filepath.split('/')
    for idx, dir in enumerate(dirs):
        if dir == "static":
            static_idx = idx
            break

    if static_idx is not None:
        return "/".join(dirs[static_idx:])


def static_url_to_path(static_url: str):
    return os.path.join('app/static/', static_url)


def get_filename_salt(n: int = 5) -> str:
    return str(uuid4())[:n]
