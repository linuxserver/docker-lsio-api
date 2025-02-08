from pydantic import BaseModel


class Image(BaseModel):
    name: str
    version: str
    category: str
    stable: bool
    deprecated: bool

class Repository(BaseModel):
    linuxserver: list[Image]

class ImagesData(BaseModel):
    repositories: Repository

class ImagesResponse(BaseModel):
    status: str
    data: ImagesData
