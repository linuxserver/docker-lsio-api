from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from keyvaluestore import KeyValueStore
from models import ImagesResponse
import json
import traceback

api = FastAPI(docs_url="/", title="LinuxServer API", redoc_url=None, version="1.0")

@api.get("/health", summary="Get the health status")
async def health():
    return "Success"

@api.get("/api/v1/images", response_model=ImagesResponse, summary="Get a list of images")
async def images():
    try:
        with KeyValueStore() as kv:
            content = json.loads(kv["images"])
            return JSONResponse(content=content)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    api.run()
