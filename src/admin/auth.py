from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from src.config import settings
from src.deps import get_current_user
from src.security import create_access_token
from typing import Any
from src import crud


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]

        user = await crud.user.authenticate(email, password)
        if user:
            access_token = create_access_token(subject=user.id)
            request.session.update({"token": access_token})

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Any:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for('admin:login'), status_code=302)
        user = await get_current_user(token)
        if not user:
            return RedirectResponse(request.url_for('admin:login'), status_code=302)
        return True


authentication_backend = AdminAuth(secret_key=settings.SECRET)
