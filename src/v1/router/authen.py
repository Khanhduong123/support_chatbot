from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.v1.schemas.schemas import UserResponseSchema, Token, CreateUserSchema
from src.v1.models.model import User
from src.v1.configs.database import bcrypt_context, db_dependency
from src.v1.services.users.auth import authenticate_user
from src.v1.services.users.token import create_access_token
from typing import Annotated

from src.v1.services.users.auth import user_dependency

from datetime import timedelta
from src.v1.services.users.auth import get_current_user


router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    """
    Xử lý đăng nhập và trả về token.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(
        username=user.name,
        user_id=user.user_id,
        expires_delta=timedelta(minutes=30),  # Thời gian hết hạn token
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponseSchema
)
async def create_user(user: CreateUserSchema, db: db_dependency):
    """
    Tạo người dùng mới và trả về thông tin người dùng.
    """
    # Mã hóa mật khẩu trước khi lưu vào cơ sở dữ liệu

    # Tạo đối tượng người dùng từ dữ liệu đầu vào
    new_user = User(
        name=user.username,  # Đảm bảo các trường khớp với model SQLAlchemy
        password=bcrypt_context.hash(user.password),  # Mã hóa mật khẩu nếu cần thiết
    )

    # Thêm người dùng vào cơ sở dữ liệu
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Lấy dữ liệu mới nhất từ cơ sở dữ liệu

    # Trả về thông tin người dùng dưới dạng Pydantic model
    return UserResponseSchema(user_id=new_user.user_id, name=new_user.name)


@router.get("/signin", response_model=UserResponseSchema)
async def signin_user(
    db: db_dependency, current_user: dict = Depends(get_current_user)
):
    user_obj = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponseSchema(user_id=user_obj.user_id, name=user_obj.name)
