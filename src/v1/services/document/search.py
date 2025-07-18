from fastapi import HTTPException
from fastapi import status
import os
import uuid
from tqdm import tqdm
from qdrant_client import QdrantClient, models
from src.v1.models.model import Document
from sqlalchemy.orm import Session
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.v1.configs.config import Config
from src.dependency import embeddings_documents_model


def split_document(user_id: int, db: Session):
    """
    Split the document into smaller chunks based on the file type.
    """
    documents_from_db = db.query(Document).filter(Document.user_id == user_id).all()

    if not documents_from_db:
        return []

    all_chunks = []

    for doc in documents_from_db:
        file_path = doc.file_path
        file_type = doc.document_type
        document_id = doc.document_id
        document_name = os.path.basename(file_path)

        # Chọn loader phù hợp
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
        elif file_type == "txt":
            loader = TextLoader(file_path)
        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)
        elif file_type == "csv":
            loader = CSVLoader(file_path)
        elif file_type == "xlsx":
            loader = UnstructuredExcelLoader(file_path)
        else:
            continue  # Bỏ qua file không hỗ trợ

        # Load và split
        documents = loader.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        # Gom tất cả chunk thành dict
        chunks = [
            {
                "user_id": user_id,
                "document_id": document_id,
                "document_name": document_name,
                "page": doc.metadata.get("page", 0) + 1,
                "content": doc.page_content,
            }
            for doc in text_splitter.split_documents(documents)
        ]

        all_chunks.extend(chunks)

    return all_chunks


class DocumentService:
    def __init__(self):
        self.client_grpc = QdrantClient(
            api_key=Config.QDRANT_API_KEY, url=Config.QDRANT_URL
        )
        self.embedding_model = embeddings_documents_model
        self.vector_size = Config.EMBEDDING_DIM
        self.batch_size = Config.BATCH_SIZE

    def create_collection(self, user_id):
        collection_name = f"collection_user_{user_id}"
        if not self.client_grpc.collection_exists(collection_name):
            response = self.client_grpc.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size, distance=models.Distance.COSINE
                ),
            )
            self.client_grpc.create_payload_index(
                collection_name=collection_name,
                field_name="document_name",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )
        else:
            response = {"status": "Collection already exists"}
            return response

    def add_patching_points(self, list_chunks, user_id):
        num_features = len(list_chunks)
        num_batches = (num_features + self.batch_size - 1) // self.batch_size

        for i in tqdm(range(num_batches)):
            # Split into batches
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, num_features)

            ids = [str(uuid.uuid4()) for _ in range(start_idx, end_idx)]
            payload = list_chunks[start_idx:end_idx]

            list_content = [doc["content"] for doc in payload]
            vectors = self.embedding_model.embed_documents(list_content)

            self.client_grpc.upload_collection(
                collection_name=f"collection_user_{user_id}",
                vectors=vectors,
                payload=payload,
                ids=ids,
            )

    async def delete_document(self, document_name, user_id):
        response = self.client_grpc.delete(
            collection_name=f"collection_user_{user_id}",
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_name",  # chính xác key này phải đúng kiểu string
                            match=models.MatchValue(value=document_name),
                        )
                    ]
                )
            ),
        )
        return response

    def load_and_split_documents(self, user_id: int, db: Session):
        """
        Load and split documents for a given user_id.
        """
        try:
            chunks = split_document(user_id, db)
            if not chunks:
                return []

            # Upload chunks to the search service
            self.add_patching_points(chunks, user_id)
        except Exception as e:
            print(f"Error loading and splitting documents: {e}")
            # return []

    async def delete_documents(self, document_name, user_id: int):
        """
        Delete documents for a given user_id.
        """
        try:
            await self.delete_document(document_name=document_name, user_id=user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting documents: {str(e)}",
            )
