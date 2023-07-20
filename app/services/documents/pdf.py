import fitz


class PDFViewer:
    @classmethod
    def get_text(cls, filepath: str, page_number: int | None = None) -> str | None:
        doc = fitz.open(filepath)
        if page_number is None:
            text = "\n".join((page.get_text() for page in doc))
            return text
        else:
            if page_number < len(doc):
                page = doc[page_number - 1]
                return page.get_text()

    @classmethod
    def save_cover(cls, filepath: str, cover_filepath: str) -> str:
        doc = fitz.open(filepath)
        first_page = doc[0]
        picture = first_page.get_pixmap()
        picture.save(cover_filepath)

    @classmethod
    def get_pages_count(cls, filepath: str) -> int:
        doc = fitz.open(filepath)
        return len(doc)

    @classmethod
    def get_pages_count_and_cover(cls, filepath: str, cover_filepath: str) -> int:
        doc = fitz.open(filepath)
        first_page = doc[0]
        picture = first_page.get_pixmap()
        picture.save(cover_filepath)
        return len(doc)
