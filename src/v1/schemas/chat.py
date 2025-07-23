from pydantic import BaseModel
from typing import List, Optional
# Schema cho từng document liên quan
class RelevantDocSchema(BaseModel):
    page: int
    document_name: str
    document_id: int
    content: str


# Request từ frontend gửi lên
class RequestSchema(BaseModel):
    session_id: str
    question: str
    user_id: int  # thêm nếu cần xác định người dùng


# Response gửi về frontend
class ResponseSchema(BaseModel):
    question: str
    answer: str
    relevant_docs: List[RelevantDocSchema] = []


# Lịch sử 1 câu hỏi - câu trả lời (nếu cần hiển thị lại history)
class ChatHistorySchema(BaseModel):
    question: str
    answer: str
    relevant_docs: List[RelevantDocSchema] = []


# Full thông tin một conversation (nếu cần trả hết)
class ConversationSchema(BaseModel):
    session_id: str
    conversation_id: int
    user_id: int
    history: List[ChatHistorySchema]
