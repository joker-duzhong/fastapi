from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from odmantic.session import AIOSession

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AIOSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


# @router.post("/password-recovery/{email}", response_model=schemas.Msg)
# def recover_password(email: str, db: AIOSession = Depends(deps.get_db)) -> Any:
#     """
#     Password Recovery
#     """
#     pass


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: AIOSession = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """

@router.post("/login", response_model=schemas.Msg)
async def reset_password(phone: str):
    print(phone)
    # return await crud.crud_user({phone})
    return {"msg": "successful"}