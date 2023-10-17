from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from odmantic.session import AIOSession

from app import crud, models, schemas

router = APIRouter()

@router.post("/login", response_model=schemas.Msg)
async def reset_password(phone: str):
    print(phone)
    # return await crud.crud_user({phone})
    return {"msg": "successful"}