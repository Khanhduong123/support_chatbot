import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class DatabaseSettings(BaseSettings):
    # General settings
    URL_DATABASE: str = os.getenv("URL_DATABASE")
    DATA_DIR: str = os.getenv("DATA_DIR")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")


class Config:
    # Load the QDRANT_URL from environment variables
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    if not QDRANT_URL:
        raise ValueError("QDRANT_URL environment variable is required.")

    # Load the QDRANT_API_KEY from environment variables
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    if not QDRANT_API_KEY:
        raise ValueError("QDRANT_API_KEY environment variable is required.")

    # Load EMBEDDING_DIM from environment variables, defaulting to 768 if not set
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", 1536))

    # Load BATCH_SIZE from environment variables, defaulting to 32 if not set
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", 100))

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    def __init__(self):
        # Optionally, you can add validation checks here if needed
        if not isinstance(self.EMBEDDING_DIM, int) or self.EMBEDDING_DIM <= 0:
            raise ValueError(
                f"Invalid EMBEDDING_DIM: {self.EMBEDDING_DIM}, it must be a positive integer."
            )
        if not isinstance(self.BATCH_SIZE, int) or self.BATCH_SIZE <= 0:
            raise ValueError(
                f"Invalid BATCH_SIZE: {self.BATCH_SIZE}, it must be a positive integer."
            )
