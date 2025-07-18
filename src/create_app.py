from fastapi import FastAPI
from src.v1.models.model import Base
from src.v1.configs.database import engine

from src.v1.configs.swagger import swagger_config


# Define create_app function.
# Avoid circular import by using this function
# to create FastAPI app instance.
def create_app():
    app = FastAPI(**swagger_config)
    Base.metadata.create_all(bind=engine)
    return app
