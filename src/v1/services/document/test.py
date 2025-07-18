import uuid
from src.v1.configs.config import Config
from qdrant_client import QdrantClient, models
from tqdm import tqdm


class DocumentSearch:
    def __init__(self, client_gpc: QdrantClient, model):
        self.client_grpc = client_gpc
        self.embedding_model = model
        self.collection_name = f"collection_user"
        self.vector_size = Config.EMBEDDING_DIM
        self.batch_size = Config.BATCH_SIZE

        if not self.check_collection():
            self.create_collection()

    def create_collection(self):
        response = self.client_grpc.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=1536, distance=models.Distance.COSINE
            ),
        )
        self.client_grpc.create_payload_index(
            collection_name=self.collection_name,
            field_name="document_name",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )
        return response

    def check_collection(self):
        response = self.client_grpc.collection_exists(
            collection_name=self.collection_name
        )

        return response

    def add_patching_points(self, list_chunks):
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
                collection_name=self.collection_name,
                vectors=vectors,
                payload=payload,
                ids=ids,
            )

    async def search(self, question, top_k=2):
        vectors = self.embedding_model.embed_documents([question])

        response = await self.client_grpc.async_grpc_points.Search(
            models.SearchPoints(
                collection_name=self.collection_name,
                vector=vectors[0],
                limit=top_k,
                with_payload=models.WithPayloadSelector(enable=True),
            )
        )

        results = []
        for data in response.result:
            results.append(
                {
                    "score": data.score,
                    "content": data.payload["content"].string_value,
                    "document_name": data.payload["document_name"].string_value,
                    "document_id": data.payload["document_id"].integer_value,
                    "page": data.payload["page"].integer_value,
                }
            )

        # print(results)
        return results

    def search_sync(self, question, top_k=2):
        vectors = self.embedding_model.embed_documents([question])

        response = self.client_grpc.Search(
            models.SearchPoints(
                collection_name=self.collection_name,
                vector=vectors[0],
                limit=top_k,
                with_payload=models.WithPayloadSelector(enable=True),
            )
        )

        results = []
        for data in response.result:
            results.append(
                {
                    "score": data.score,
                    "content": data.payload["content"].string_value,
                    "document_name": data.payload["document_name"].string_value,
                    "document_id": data.payload["document_id"].integer_value,
                    "page": data.payload["page"].integer_value,
                }
            )

        # print(results)
        return results

    async def delete_document(self, document_name):
        response = self.client_grpc.delete(
            collection_name=self.collection_name,
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
