from fastapi import Depends, Request, HTTPException
from fastapi_authtools.exceptions import raise_permissions_error
from uuid import uuid4
import os
from langdetect import detect

from app.api.dependencies import get_document_repository
from app.db.repositories import DocumentRepository
from app.services.tts import synth_audio
from app.services.documents import get_text
from app.services.files import static_url_to_path
from app.services.patterns import check_text


async def get_document(
        request: Request,
        document_id: str,
        document_repo: DocumentRepository = Depends(get_document_repository),
        page: int | None = None
):
    document = await document_repo.get(document_id)
    if document.user_id != request.user.id:
        raise_permissions_error()
    if document is None:
        raise HTTPException(status_code=404, detail="Document is not found.")
    yield document
    if page is None:
        await document_repo.update_time_opened(document_id)
    else:
        await document_repo.update_time_opened_and_page(document_id, page)


async def get_synth_audio_filepath(
        request: Request,
        document=Depends(get_document),
        page: int | None = None
):
    fullpath = os.path.join(
        request.app.state.STATIC_DIR, request.user.id, str(uuid4()) + ".mp3"
    )
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    lang = detect(text)
    if check_text(text):
        await synth_audio(text, fullpath, lang)
        yield {"status": 200, "filepath": fullpath}
        os.remove(fullpath)
    else:
        yield {"status": 400, "detail": "Cannot find the text."}
