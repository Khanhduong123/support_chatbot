from fastapi import APIRouter
from src.v1.router.user import router as user_router
from src.v1.router.document import router as document_router
from src.v1.router.authen import router as auth_router

# Tạo API version 1
api_v1_router = APIRouter(prefix="/v1")

# Bao gồm user_router vào api_v1_router với prefix "/users" và tags "users"

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(user_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(document_router, prefix="/documents", tags=["Documents"])
