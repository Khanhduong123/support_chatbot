from fastapi import APIRouter, Depends, HTTPException, status
from src.v1.schemas.schemas import UserResponseSchema, UserVerify
from src.v1.models.model import User
from src.v1.configs.database import get_db
from src.v1.services.users.token import get_user_from_token
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_user_from_token)]


@router.get("/", response_model=UserResponseSchema)
async def read_my_user(user: user_dependency, db: Session = Depends(get_db)):
    user_obj = db.query(User).filter(User.user_id == user["user_id"]).first()
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponseSchema(user_id=user_obj.user_id, name=user_obj.name)


@router.put("/change-password")
async def change_password(
    user_vertify: UserVerify, user: user_dependency, db: Session = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    user_model = db.query(User).filter(User.user_id == user.get("user_id")).first()
    if not bcrypt_context.verify(user_vertify.password, user_model.password):
        raise HTTPException(status_code=401, detail="Password not match")

    user_model.password = bcrypt_context.hash(user_vertify.new_password)
    db.add(user_model)
    db.commit()
