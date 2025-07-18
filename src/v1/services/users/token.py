from datetime import datetime, timedelta, timezone
from src.v1.configs.config import DatabaseSettings
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session
from src.v1.models.model import User
from src.v1.configs.database import get_db
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from typing import Annotated


settings = DatabaseSettings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")  # Đường dẫn đến token


def create_access_token(username: str, user_id: int, expires_delta: timedelta):

    encode = {
        "sub": username,
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }

    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_user_from_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        # Giải mã JWT
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        name: str = payload.get("sub")  # 'sub' là tên người dùng (hoặc email)

        if user_id is None or name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or missing user info",
            )

        # Truy vấn người dùng trong cơ sở dữ liệu
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {"username": name, "user_id": user_id}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


async def get_user_id_from_token(
    token: str = Depends(get_user_from_token), db: Session = Depends(get_db)
):
    """
    Lấy user_id từ token.
    Giả sử `get_user_from_token` trả về một đối tượng user hoặc dict chứa `user_id`.
    """
    if not token:
        raise HTTPException(status_code=403, detail="Token là bắt buộc")

    user = await get_user_from_token(token, db)

    if not user or "user_id" not in user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    return user["user_id"]


user_dependency = Annotated[dict, Depends(get_user_from_token)]
