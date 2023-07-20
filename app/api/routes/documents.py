from fastapi import APIRouter, Request, File, Depends, UploadFile
from fastapi.responses import FileResponse
from fastapi_authtools import login_required
import os

from app.api.dependencies import (
    get_document_repository,
    get_document,
    get_synth_audio_filepath,

)
from app.db.repositories import DocumentRepository
from app.services import (
    get_name_and_extension,
    path_to_static_url,
    static_url_to_path,
    check_text,

)
from app.services.documents import (
    get_pages_count_and_cover,
    get_text,

)


documents_router = APIRouter(prefix='/documents')


@documents_router.get("/my-documents")
@login_required
async def my_documents(
        request: Request,
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    documents = await document_repo.filter(user_id=request.user.id)
    return documents


@documents_router.post("/upload-document")
@login_required
async def upload_document(
        request: Request,
        document_file: UploadFile = File(),
        document_repo: DocumentRepository = Depends(get_document_repository),
):
    user_dirpath = f"{request.user.id}"
    user_fullpath = os.path.join(request.app.state.STATIC_DIR, user_dirpath)
    if not os.path.exists(user_fullpath):
        os.makedirs(user_fullpath)

    filename, extension = get_name_and_extension(document_file.filename)

    if extension != "pdf":
        return None

    dirpath = f"{request.user.id}/{document_file.filename}"
    fullpath = os.path.join(request.app.state.STATIC_DIR, dirpath)
    with open(fullpath, "wb") as file:
        file.write(await document_file.read())
    cover_dirpath = f"{request.user.id}/{filename}_cover.png"
    cover_fullpath = os.path.join(request.app.state.STATIC_DIR, cover_dirpath)
    pages_count = get_pages_count_and_cover(fullpath, cover_fullpath)
    document = await document_repo.create(
        title=filename,
        extension=extension,
        document_url=path_to_static_url(fullpath),
        user_id=request.user.id,
        pages=pages_count,
        current_page=0,
        cover_url=path_to_static_url(cover_fullpath),

    )
    return document


@documents_router.get("/{document_id}")
@login_required
async def document_get(
        request: Request,
        document=Depends(get_document)
):
    return document


@documents_router.post("/{document_id}/download")
@login_required
async def upload_document(
        request: Request,
        document=Depends(get_document)
):
    return FileResponse(
        path=static_url_to_path(document.document_url),
        filename=f"{document.title}.{document.extension}",
    )


@documents_router.get("/{document_id}/text")
@login_required
async def get_document_text(
        request: Request,
        document=Depends(get_document),
        page: int | None = None
):
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    if check_text(text):
        return {"text": text}
    else:
        return {"detail": "Cannot find text to read."}


@documents_router.get("/{document_id}/voice")
@login_required
async def get_document_voice(
        request: Request,
        document=Depends(get_document),
        voice_filepath=Depends(get_synth_audio_filepath),
        page: int | None = None
):
    if voice_filepath is None:
        return {"detail": "Cannot find text to read."}
    return FileResponse(
        path=voice_filepath,
        filename=f"{document.title}_page{page}.wav" if page is not None else f"{document.title}.wav"
    )
