from pydantic import BaseModel

# Increment when updating schema
SCHEMA_VERSION = "1"

class Tag(BaseModel):
    tag: str
    desc: str

class Architecture(BaseModel):
    arch: str
    tag: str

class Image(BaseModel):
    name: str
    github_url: str
    project_url: str
    description: str
    version: str
    version_timestamp: str
    category: str
    stable: bool
    deprecated: bool
    stars: int
    tags: list[Tag]
    architectures: list[Architecture]

class Repository(BaseModel):
    linuxserver: list[Image]

class ImagesData(BaseModel):
    repositories: Repository

class ImagesResponse(BaseModel):
    status: str
    data: ImagesData
