from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from keyvaluestore import KeyValueStore
from models import ImagesResponse
from pydantic import ValidationError
import json
import traceback

api = FastAPI(docs_url="/", title="LinuxServer API", redoc_url=None, version="1.0")

@api.get("/health", summary="Get the health status")
async def health():
    return "Success"

async def get_images():
    with KeyValueStore() as kv:
        return kv["images"]

@api.get("/api/v1/images", response_model=ImagesResponse, summary="Get a list of images", response_model_exclude_none=True)
async def images(include_config: bool = False, include_deprecated: bool = False):
    try:
        response = await get_images()
        image_response = ImagesResponse.model_validate_json(response)
        if not include_deprecated:
            image_response.exclude_deprecated()
        if not include_config:
            image_response.exclude_config()
        return image_response
    except ValidationError:
        print(traceback.format_exc())
        response = await get_images()
        content = json.loads(response)
        return JSONResponse(content=content)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    api.run()
