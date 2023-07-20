from uuid import uuid4

from fastapi import Depends, Request, HTTPException
from fastapi_authtools.exceptions import raise_permissions_error
import os

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
):
    document = await document_repo.get(document_id)
    if document.user_id != request.user.id:
        raise_permissions_error()
    if document is None:
        raise HTTPException(status_code=404, detail="Document is not found.")
    return document


async def get_synth_audio_filepath(
        request: Request,
        document=Depends(get_document),
        page: int | None = None
):
    fullpath = os.path.join(
        request.app.state.STATIC_DIR, request.user.id, str(uuid4()) + ".wav"
    )
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    if check_text(text):
        synth_audio(text, fullpath)
        yield fullpath
        os.remove(fullpath)
    else:
        yield None
