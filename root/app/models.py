from pydantic import BaseModel

# Increment when updating schema
IMAGES_SCHEMA_VERSION = 1

class Tag(BaseModel):
    tag: str
    desc: str

class Architecture(BaseModel):
    arch: str
    tag: str

class Changelog(BaseModel):
    date: str
    desc: str

class Volume(BaseModel):
    path: str
    host_path: str
    desc: str
    optional: bool

class Port(BaseModel):
    external: str
    internal: str
    desc: str
    optional: bool

class EnvVar(BaseModel):
    name: str
    value: str
    desc: str
    optional: bool

class EnvVar(BaseModel):
    name: str
    value: str
    desc: str
    optional: bool

class Custom(BaseModel):
    name: str
    name_compose: str
    value: str | list[str]
    desc: str
    optional: bool

class SecurityOpt(BaseModel):
    run_var: str
    compose_var: str
    desc: str
    optional: bool

class Device(BaseModel):
    path: str
    host_path: str
    desc: str
    optional: bool

class Cap(BaseModel):
    cap_add: str
    desc: str
    optional: bool

class Hostname(BaseModel):
    hostname: str
    desc: str
    optional: bool

class MacAddress(BaseModel):
    mac_address: str
    desc: str
    optional: bool

class Image(BaseModel):
    name: str
    github_url: str
    project_url: str | None
    project_logo: str | None
    application_setup: str
    description: str
    version: str
    version_timestamp: str
    category: str
    stable: bool
    deprecated: bool | None
    stars: int
    readonly_supported: bool | None
    nonroot_supported: bool | None
    privileged: bool | None
    networking: str | None
    hostname: Hostname | None
    mac_address: MacAddress | None
    tags: list[Tag]
    architectures: list[Architecture]
    env_vars: list[EnvVar] | None
    volumes: list[Volume] | None
    ports: list[Port] | None
    custom: list[Custom] | None
    security_opt: list[SecurityOpt] | None
    devices: list[Device] | None
    caps: list[Cap] | None
    changelog: list[Changelog] | None

class Repository(BaseModel):
    linuxserver: list[Image]

class ImagesData(BaseModel):
    repositories: Repository

class ImagesResponse(BaseModel):
    status: str
    last_updated: str
    data: ImagesData
