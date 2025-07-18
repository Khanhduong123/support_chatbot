import os
from src.v1.models.model import User
from src.v1.configs.database import bcrypt_context
from typing import Annotated
from fastapi import Depends, HTTPException, status
from src.v1.services.users.token import oauth2_scheme
from jose import jwt
from jose.exceptions import JWTError


def authenticate_user(username: str, password: str, db):
    """
    Xác thực người dùng với tên đăng nhập và mật khẩu.
    """
    user = db.query(User).filter(User.name == username).first()
    if not user or not bcrypt_context.verify(password, user.password):
        return False
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )

        username: str = payload.get(
            "sub"
        )  # lấy từ def create_access_token encode['sub']
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return {"username": username, "id": user_id, "user_role": user_role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


user_dependency = Annotated[dict, Depends(get_current_user)]
