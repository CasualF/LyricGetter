from asyncio import sleep
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import EmailStr, UUID4, TypeAdapter

from src import crud
from src.config import settings
from src.account.utils import send_new_account_email
from src.account.schemas import User, UserCreate, UserUpdate, Token, UserResponse
from src.account.models import Account
from src.security import create_access_token
from src.deps import get_current_superuser, get_current_user

from fastapi_cache.decorator import cache

router = APIRouter()


@router.get('/', response_model=list[User])
@cache(expire=600)
async def retrieve_users(
        current_user:  Account = Depends(get_current_superuser)
) -> list[User]:
    users = await crud.user.get_list()
    return users


@router.post("/register", status_code=201, response_model=UserResponse)
async def user_register(user_data: UserCreate, background_tasks: BackgroundTasks):
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await crud.user.get_by_email(email=user_data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    if user_data.is_superuser:
        raise HTTPException(status_code=400, detail="Can't create a superuser")

    user = await crud.user.create(user_data)
    response = {"msg": "Account successfully created!", "data": user}
    try:
        if settings.EMAILS_ENABLED and user_data.email:
            background_tasks.add_task(send_new_account_email,
                                      email_to=user_data.email,
                                      username=user_data.email,
                                      password=user_data.password,
                                      code=str(user.activation_code))
    except:
        return {"msg": "Email was not sent but account created", 'data': user}
    return response


@router.post("/grant-admin")
async def superuser_register(permission_pass: str,
                             user_id: int = None,
                             current_user: Account = Depends(get_current_user)) -> str:
    if permission_pass != settings.PERMISSION_PASS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Incorrect permission password!')
    user_id = user_id if user_id else current_user.id
    superuser = await crud.user.make_admin(user_id)

    return f"{superuser.email} is now an admin!"


@router.post('/login', response_model=Token)
async def login_jwt_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crud.user.authenticate(email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect email or password')
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail='Inactive user')

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post('/logout', response_model=str)
async def logout_user(response: Response):
    # response.delete_cookie('access_token')
    return 'User successfully logged out'


@router.get('/profile/me', response_model=User)
async def retrieve_myself(current_user: Account = Depends(get_current_user)):
    user = current_user
    return user


@router.get('/profile/{email}', response_model=User | None)
async def retrieve_by_email(email: EmailStr):
    user = await crud.user.get_by_email(email)
    if not user:
        raise HTTPException(detail='User not found', status_code=status.HTTP_404_NOT_FOUND)
    return user


@router.delete('/profile/{email}', status_code=204)
async def delete_by_email(email: EmailStr, current_user: Account = Depends(get_current_superuser)):
    await crud.user.destroy(email)
    response = {'msg': "Account successfully deleted!"}
    return response


@router.put('/profile/{email}', response_model=User)
async def update_by_email(email: EmailStr,
                          update_data: UserUpdate,
                          current_user: User = Depends(get_current_user)):
    user = await crud.user.get_by_email(email=email)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    if update_data.is_superuser != user.is_superuser:
        raise HTTPException(status_code=400, detail="Superuser status can't be changed")
    if current_user.email != email:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only owner or admin have the privileges for this action!")
    response = await crud.user.update(email=email, obj_in=update_data)
    return response


@router.post('/activate/{user_code}')
async def activate_user(user_code: UUID4):
    await crud.user.activate_user(code=user_code)
    return 'User successfully activated!'


@router.get('/activate/{user_code}')
async def activate_user(user_code: UUID4):
    await crud.user.activate_user(code=user_code)
    return 'User successfully activated!'
