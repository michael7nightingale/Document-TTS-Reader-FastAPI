from .main import main_router
from .auth import auth_router
from .documents import documents_router


__api_routers__ = (
    main_router,
    auth_router,
    documents_router,

)
