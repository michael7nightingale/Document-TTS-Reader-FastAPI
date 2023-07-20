from fastapi import Depends
from typing import Type, Callable

from .database import get_repository
from app.db.repositories import (
    UserRepository,
    DocumentRepository,

)
from ...db.repositories.base import BaseRepository


def get_base_repository(repo_type: Type[BaseRepository]) -> Callable:
    """Repository dependency fabric function."""
    def inner(repo: Type[BaseRepository] = Depends(get_repository(repo_type))):
        return repo
    return inner


get_user_repository = get_base_repository(UserRepository)
get_document_repository = get_base_repository(DocumentRepository)
