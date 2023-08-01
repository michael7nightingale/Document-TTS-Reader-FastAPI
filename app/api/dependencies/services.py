from fastapi import Request

from app.db.services import UserService, DocumentService


def get_base_service(service_type):
    def inner(request: Request):
        service = service_type(db=request.app.state.db)
        return service
    return inner


get_user_service = get_base_service(UserService)
get_document_service = get_base_service(DocumentService)
