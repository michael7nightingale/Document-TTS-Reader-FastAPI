from fastapi import APIRouter, Request, File, Depends, UploadFile, Path, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi_authtools import login_required
from uuid import uuid4
import os
from shutil import rmtree

from app.db.repositories import DocumentRepository
from app.api.dependencies import (
    get_document_repository,
    get_document,
    get_synth_audio_filepath,

)
from app.models.schemas import Document
from app.services import (
    get_name_and_extension,
    static_url_to_path,
    check_text,

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
    user_path = f"{request.user.id}"
    user_fullpath = os.path.join(request.app.state.STATIC_DIR, user_path)
    if not os.path.exists(user_fullpath):
        os.makedirs(user_fullpath)

    # saving document
    document_uuid = str(uuid4())
    filename, extension = get_name_and_extension(document_file.filename)
    if extension not in ("pdf", ):
        return JSONResponse(
            content={"detail": f"{extension} not in available extensions: `pdf`."},
            status_code=400
        )
    document_path = os.path.join(user_path, document_uuid)
    document_fullpath = os.path.join(request.app.state.STATIC_DIR, document_path)
    os.makedirs(document_fullpath)
    pdf_file_path = os.path.join(document_path, f"{filename}.{extension}")
    pdf_file_fullpath = os.path.join(request.app.state.STATIC_DIR, pdf_file_path)
    with open(pdf_file_fullpath, "wb") as file:
        file.write(await document_file.read())

    # saving document`s cove image (1st page)
    cover_path = os.path.join(document_path, f"{filename}_cover.png")
    cover_fullpath = os.path.join(request.app.state.STATIC_DIR, cover_path)
    # creating document instance
    pages_count = get_pages_count_and_cover(extension, pdf_file_fullpath, cover_fullpath)
    document = await document_repo.create(
        id=document_uuid,
        title=filename,
        extension=extension,
        document_url=pdf_file_path,
        user_id=request.user.id,
        pages=pages_count,
        current_page=0,
        cover_url=cover_path
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
async def document_delete(
        request: Request,
        document_id: str = Path(),
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    """Delete document from db and its files."""
    await document_repo.delete(document_id)
    document_fullpath = os.path.join(request.app.state.STATIC_DIR, request.user.id, document_id)
    if os.path.exists(document_fullpath):
        rmtree(document_fullpath)
        return {"detail": f"Document {document_id} is deleted."}
    return {"detail": "Document is already deleted."}


@documents_router.patch("/my/{document_id}")
@login_required
async def document_update(
        request: Request,
        document_id: str = Path(),
        update_data: Document = Body(),
        document_repo: DocumentRepository = Depends(get_document_repository)
):
    """Update document."""
    await document_repo.update(document_id, **update_data.model_dump())
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
    if not (0 < page <= document.pages):
        return JSONResponse(
            content={'detail': f"Page is out of range: from 1 to {document.pages}."},
            status_code=400
        )
    text = get_text(
        extension=document.extension,
        filepath=static_url_to_path(document.document_url),
        page_number=page
    )
    if text is None or not check_text(text):
        return {"detail": "Cannot find text to read."}
    return {"text": text}


@documents_router.get("/my/{document_id}/voice")
@login_required
async def get_document_voice(
        request: Request,
        page: int,
        document=Depends(get_document),
        voice_filepath: dict = Depends(get_synth_audio_filepath)
):
    """Endpoint for getting voice tts from the document CURRENT PAGE."""
    if voice_filepath["status_code"] != 200:
        return JSONResponse(
            content=voice_filepath['content'],
            status_code=voice_filepath['status_code']
        )
    return FileResponse(
        path=voice_filepath['filepath'],
        filename=f"{document.title}_page{page}.wav" if page is not None else f"{document.title}.wav"
    )
