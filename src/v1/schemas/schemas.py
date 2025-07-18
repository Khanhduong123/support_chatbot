from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    username: str
    password: str


class UserResponseSchema(BaseModel):
    user_id: int
    name: str

    class Config:
        from_attributes = True


class DocumentResponseSchema(BaseModel):
    document_id: int
    user_id: int
    document_name: str
    document_type: str
    document_size: int
    file_path: str
    created_at: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class UserVerify(BaseModel):
    password: str
    new_password: str
