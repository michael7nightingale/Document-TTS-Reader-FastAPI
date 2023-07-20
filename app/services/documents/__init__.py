from .pdf import PDFViewer


extensions = {
    "pdf": PDFViewer,

}


def match_extension(func):
    def inner(extension: str, *args, **kwargs):
        if extension in extensions:
            return getattr(PDFViewer, func.__name__)(*args, **kwargs)
    return inner


@match_extension
def get_text(filepath: str, page_number: int | None = None) -> str | None:
    pass


@match_extension
def save_cover(filepath: str, cover_filepath: str) -> str:
    pass


@match_extension
def get_pages_count(filepath: str) -> int:
    pass


@match_extension
def get_pages_count_and_cover(filepath: str, cover_filepath: str) -> int:
    pass
