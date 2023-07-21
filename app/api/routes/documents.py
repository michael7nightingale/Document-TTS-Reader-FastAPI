from fastapi import APIRouter, Request, File, Depends, UploadFile, Path, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi_authtools import login_required
from uuid import uuid4
import os

from app.db.repositories import DocumentRepository
from app.api.dependencies import (
    get_document_repository,
    get_document,
    get_synth_audio_filepath,

)
from app.models.schemas import DocumentUpdate
from app.services import (
    get_name_and_extension,
    path_to_static_url,
    static_url_to_path,
    check_text, get_filename_salt,

)
from app.services.documents import (
    get_pages_count_and_cover,
    get_text,

)


documents_router = APIRouter(prefix='/documents')


@documents_router.get("/my/all")
@login_required
async def my_documents(
        request: Request,
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    """Endpoint for all documents of the user."""
    documents = await document_repo.filter(user_id=request.user.id)
    return documents


@documents_router.post("/upload-document")
@login_required
async def upload_document(
        request: Request,
        document_file: UploadFile = File(),
        document_repo: DocumentRepository = Depends(get_document_repository),
):
    """Endpoint for uploading document to the collection."""
    # check if user`s documents` folder exists
    user_dirpath = f"{request.user.id}"
    user_fullpath = os.path.join(request.app.state.STATIC_DIR, user_dirpath)
    if not os.path.exists(user_fullpath):
        os.makedirs(user_fullpath)

    # saving document
    document_uuid = str(uuid4())
    filename, extension = get_name_and_extension(document_file.filename)
    if extension not in ("pdf", ):
        return JSONResponse(
            content={"detail": f"{Exception} not in available extensions: `pdf`."},
            status_code=400
        )
    dirpath = f"{request.user.id}/{document_file.filename}"
    fullpath = os.path.join(request.app.state.STATIC_DIR, dirpath)

    # if this filepath is busy
    salt_degree = 3
    while os.path.exists(fullpath):
        salt = get_filename_salt(salt_degree)
        filename += f"_{salt}"
        dirpath = f"{request.user.id}/{document_uuid}/{filename}.{extension}"
        fullpath = os.path.join(request.app.state.STATIC_DIR, dirpath)
        salt_degree += 1

    with open(fullpath, "wb") as file:
        file.write(await document_file.read())

    # saving document`s cove image (1st page)
    cover_dirpath = f"{request.user.id}/{document_uuid}/{filename}_cover.png"
    cover_fullpath = os.path.join(request.app.state.STATIC_DIR, cover_dirpath)
    # creating document instance
    pages_count = get_pages_count_and_cover(extension, fullpath, cover_fullpath)
    document = await document_repo.create(
        id=document_uuid,
        title=filename,
        extension=extension,
        document_url=path_to_static_url(fullpath),
        user_id=request.user.id,
        pages=pages_count,
        current_page=0,
        cover_url=path_to_static_url(cover_fullpath),

    )
    return document


@documents_router.get("/my/{document_id}")
@login_required
async def document_get(
        request: Request,
        document=Depends(get_document)
):
    """Get single document information."""
    return document


@documents_router.delete("/my/{document_id}")
@login_required
async def document_get(
        request: Request,
        document_id: str = Path(),
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    """Get single document information."""
    await document_repo.delete(document_id)
    return {"detail": f"Document {document_id} is deleted."}


@documents_router.patch("/my/{document_id}")
@login_required
async def document_get(
        request: Request,
        document_id: str = Path(),
        update_data: DocumentUpdate = Body(),
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    """Get single document information."""
    await document_repo.update(document_id, **update_data.dict())
    return {"detail": f"Document {document_id} is updated."}


@documents_router.post("/my/{document_id}/download")
@login_required
async def download_document(
        request: Request,
        document=Depends(get_document)
):
    """Download a single document."""
    return FileResponse(
        path=static_url_to_path(document.document_url),
        filename=f"{document.title}.{document.extension}",
    )


@documents_router.get("/my/{document_id}/text")
@login_required
async def get_document_text(
        request: Request,
        document=Depends(get_document),
        page: int | None = None
):
    """Endpoint for getting text from the document."""
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    if check_text(text):
        return {"text": text}
    else:
        return {"detail": "Cannot find text to read."}


@documents_router.get("/my/{document_id}/voice")
@login_required
async def get_document_voice(
        request: Request,
        page: int,
        document=Depends(get_document),
        voice_filepath: dict = Depends(get_synth_audio_filepath)
):
    """Endpoint for getting voice tts from the document CURRENT PAGE."""
    if voice_filepath["status"] != 200:
        return JSONResponse(
            content=voice_filepath['detail'],
            status_code=voice_filepath['status_code']
        )
    return FileResponse(
        path=voice_filepath['filepath'],
        filename=f"{document.title}_page{page}.wav" if page is not None else f"{document.title}.wav"
    )
