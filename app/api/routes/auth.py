from fastapi import APIRouter, Body, Request, Depends, Path
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi_authtools import login_required
from fastapi_authtools.models import UsernamePasswordToken
from fastapi_authtools.exceptions import raise_invalid_credentials

from app.api.dependencies import get_user_register_data, get_user_service
from app.models.schemas import UserRegister, UserCustomModel, UserShow
from app.core.config import get_app_settings
from app.db.services import UserService
from app.services import generate_token, confirm_token
from app.tasks.email import send_message_task


auth_router = APIRouter(
    prefix='/auth'
)


@auth_router.get('/github-login/')
async def github_login():
    """Login with GitHub."""
    return RedirectResponse(get_app_settings().github_login_url, status_code=303)


@auth_router.get("/github-got")
async def github_get(code: str):
    """Add access token from GitHub to cookies"""
    return {"access_token": code}


@auth_router.post('/token')
async def get_token(
        request: Request,
        user_token_data: UsernamePasswordToken = Body(),
        user_service: UserService = Depends(get_user_service)
):
    """Token get view."""
    print(await user_service.all())
    user = await user_service.login(
        **user_token_data.model_dump()
    )
    if user is None:
        raise_invalid_credentials()
    user_model = UserCustomModel(**user, id=str(user['_id']))
    token = request.app.state.auth_manager.create_token(user_model)
    return {"access_token": token}


@auth_router.post("/register")
async def register(
        request: Request,
        user_data: UserRegister = Depends(get_user_register_data),
        user_service: UserService = Depends(get_user_service)
):
    """Registration POST view."""
    new_user = await user_service.register(user_data)
    if new_user is None:
        return JSONResponse(
            content={"detail": "Data is invalid."},
            status_code=400
        )
    token = generate_token(email=new_user['email'])
    link = str(request.base_url) + "api/v1/auth/activation/" + f"{new_user['_id']}/" + token
    message = f"""Finish registration by following the link:
                  {link}"""
    send_message_task.run(
        "User activation.", new_user['email'], message
    )

    return f"Activation link is send on email {new_user['email']}"


@auth_router.get("/activation/{user_id}/{token}")
async def activate(
        request: Request,
        user_id: str = Path(),
        token: str = Path(),
        user_service: UserService = Depends(get_user_service)
):
    """Registration POST view."""
    if confirm_token(token) is not None:
        user = await user_service.activate(user_id)
        if user is not None:
            return "User is activated."
    return JSONResponse(
        content={"detail": "Something went wrong."},
        status_code=400
    )


@auth_router.get("/me", response_model=UserShow)
@login_required
async def me(request: Request):
    return request.user
