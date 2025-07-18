import os
import uvicorn
from src import api_v1_router
from src.create_app import create_app

app = create_app()
app.include_router(api_v1_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.environ.get("PORT", 8000))
