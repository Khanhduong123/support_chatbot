import os
import shutil
from fastapi import APIRouter, HTTPException, status, UploadFile, Depends
from src.v1.services.document.search import DocumentService
from src.v1.models.model import Document
from src.v1.configs.database import db_dependency
from src.v1.configs.config import DatabaseSettings
from pathlib import Path
from datetime import datetime
from fastapi.responses import JSONResponse
from src.v1.services.users.token import get_user_from_token, oauth2_scheme
import time


router = APIRouter()
settings = DatabaseSettings()
document_service = DocumentService()
UPLOAD_DIR = Path(settings.DATA_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile, db: db_dependency, token: str = Depends(oauth2_scheme)
):
    """
    Tải lên tài liệu và lưu vào cơ sở dữ liệu dựa trên user_id lấy từ JWT token.
    Hỗ trợ: PDF, TXT, Word, Excel, CSV.
    """

    user = await get_user_from_token(token, db)
    user_id = user["user_id"]

    # Các loại file hợp lệ
    valid_content_types = {
        "application/pdf": "pdf",
        "text/plain": "txt",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",  # .docx
        "application/msword": "word",  # .doc
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",  # .xlsx
        "application/vnd.ms-excel": "excel",  # .xls
        "text/csv": "csv",  # .csv
    }

    if file.content_type not in valid_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, TXT, Word, Excel, or CSV files are supported",
        )

    subfolder = valid_content_types[file.content_type]
    os.makedirs(UPLOAD_DIR / subfolder, exist_ok=True)

    file_path = UPLOAD_DIR / subfolder / file.filename

    try:
        with open(file_path, "wb") as out_file:
            shutil.copyfileobj(file.file, out_file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    document_size = os.path.getsize(file_path)

    new_document = Document(
        user_id=user_id,
        document_name=file.filename,
        document_type=subfolder,
        document_size=document_size,
        file_path=str(file_path),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    document_service.create_collection(user_id=user_id)

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Upload successfully",
            "filename": file.filename,
            "document_id": new_document.document_id,
            "file_path": str(file_path),
        },
    )


@router.get("/{user_id}")
async def get_documents(
    user_id: int, db: db_dependency, token: str = Depends(oauth2_scheme)
):
    """
    Lấy danh sách tài liệu của người dùng dựa trên user_id từ JWT token
    """
    user = await get_user_from_token(token, db)
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access these documents",
        )

    documents = db.query(Document).filter(Document.user_id == user_id).all()
    return documents


@router.delete("/{user_id}")
async def delete_documents(
    user_id: int, db: db_dependency, token: str = Depends(oauth2_scheme)
):
    """
    Xóa tài liệu của người dùng dựa trên user_id từ JWT token
    """
    # Kiểm tra quyền của người dùng
    user = await get_user_from_token(token, db)
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete these documents",
        )

    # Fetch documents related to user
    documents = db.query(Document).filter(Document.user_id == user_id).all()

    # Extract document names to delete from vector db
    for doc in documents:  # Lấy document_name thay vì document_id
        print(f"Deleting documents with names: {doc.document_name}")
        # # Xóa tài liệu từ Qdrant theo document_name
        # for name in document_names:
        response = await document_service.delete_documents(
            document_name=doc.document_name, user_id=user_id
        )  # Truyền document_name vào delete_document

        print(f"Response from delete_document: {response}")
    # Delete file paths
    file_paths = [doc.file_path for doc in documents if doc.file_path]

    # Xóa các bản ghi trong DB
    db.query(Document).filter(Document.user_id == user_id).delete()
    db.commit()

    # Xóa file từ hệ thống tệp
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error deleting file {path}: {e}")

    db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "All documents deleted successfully"},
    )


@router.post("/train/{user_id}")
async def train_documents(
    user_id: int, db: db_dependency, token: str = Depends(oauth2_scheme)
):
    """
    Train documents for a given user by loading and splitting them,
    then uploading to the vector database.
    """
    # Validate the user with the token
    user = await get_user_from_token(token, db)
    if user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to train these documents",
        )

    try:
        # Call the DocumentService to process the documents
        document_service.load_and_split_documents(user_id, db)

        return {"message": "Documents processed successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing documents: {str(e)}",
        )
