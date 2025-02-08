from fastapi import FastAPI
from keyvaluestore import KeyValueStore
from models import ImagesResponse, ImagesData

api = FastAPI(docs_url="/")

@api.get("/health", summary="Get the health status")
async def health():
    return "Success"

@api.get("/api/v1/images", response_model=ImagesResponse, summary="Get a list of images")
async def images():
    with KeyValueStore() as kv:
        return ImagesResponse(status="OK", data=ImagesData.model_validate_json(kv["images"]))

if __name__ == "__main__":
    api.run()
