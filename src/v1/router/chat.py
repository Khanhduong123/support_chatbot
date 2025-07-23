from fastapi import APIRouter, HTTPException, status, Depends
from src.v1.schemas.chat import RequestSchema, ResponseSchema
from src.v1.services.chat.chat_service import ChatService
from src.v1.services.users.token import get_user_from_token, oauth2_scheme
from src.v1.configs.database import db_dependency


router = APIRouter()
chat_service = ChatService()


@router.post("/get_answer", response_model=ResponseSchema)
async def get_answer(request: RequestSchema,  db: db_dependency, token: str = Depends(oauth2_scheme)):
    """
    Nhận câu trả lời từ mô hình dựa trên câu hỏi và lịch sử trò chuyện.
    """
    user_id = get_user_from_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    result = await chat_service.get_answer(
        db=db,
        user_id=user_id,
        session_id=request.session_id,
        question=request.question
    )
    return result