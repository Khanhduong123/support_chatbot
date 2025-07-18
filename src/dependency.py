from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from src.v1.services.document.test import DocumentSearch
from src.v1.configs.config import Config

document_config = Config()

client_qdrant = QdrantClient(
    url=document_config.QDRANT_URL,
    prefer_grpc=True,
    api_key=document_config.QDRANT_API_KEY,
)

embeddings_documents_model = OpenAIEmbeddings(
    model="text-embedding-3-small", dimensions=document_config.EMBEDDING_DIM
)

document_search = DocumentSearch(
    client_gpc=client_qdrant, model=embeddings_documents_model
)
