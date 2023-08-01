from fastapi import Depends, Request, HTTPException
from fastapi_authtools.exceptions import raise_permissions_error
from uuid import uuid4
import os
from langdetect import detect

from app.api.dependencies.services import get_document_service
from app.services.tts import synth_audio
from app.services.documents import get_text
from app.services.files import static_url_to_path
from app.services.patterns import check_text
from app.db.services import DocumentService


async def get_document(
        request: Request,
        document_id: str,
        page: int | None = None,
        document_service: DocumentService = Depends(get_document_service)
):
    document = await document_service.get(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document is not found.")
    if document.user_id != request.user.id:
        raise_permissions_error()
    yield document
    if page is None or not (0 < page <= document.pages):
        await document_service.update_time_opened(document_id)
    else:
        await document_service.update_time_opened_and_page(document_id, page)


async def get_synth_audio_filepath(
        request: Request,
        document=Depends(get_document),
        page: int | None = None
):
    if not (0 < page <= document.pages):
        yield {"status_code": 400, "content": {'detail': f"Page is out of range: from 1 to {document.pages}."}}
        return
    fullpath = os.path.join(
        request.app.state.STATIC_DIR, request.user.id, str(uuid4()) + ".mp3"
    )
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    if text is None or not check_text(text):
        yield {"status_code": 400, "content": {'detail': "Cannot find the text."}}
        return
    lang = detect(text)
    await synth_audio(text, fullpath, lang)
    yield {"status_code": 200, "filepath": fullpath}
    os.remove(fullpath)
