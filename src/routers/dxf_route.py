from fastapi import APIRouter, UploadFile
from utils import unique
from utils import dxf
from pydantic import BaseModel
from fastapi.responses import FileResponse
from utils.dxf_v1 import extract
from utils.dxf_v1 import draw
from utils.dxf_v1 import generate
from typing import Optional


router = APIRouter()

class Triple(BaseModel):
    code: int
    offset: int
    category: int

class Position(BaseModel):
    x: float
    y: float
    z: float

class Coordinate(BaseModel):
    entity_type: str | None = None
    layer: str | None = None
    color: int | None = None
    aci: int | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None
    position: Position | None = None
    height: float | None = None
    rotation: float | None = None
    text: str | None = None
    closed: bool | None = None
    vertices: list[Position] | None = None
    start: Position | None = None
    end: Position | None = None

class Coordinates(BaseModel):
    coordinates: list[Coordinate]
    coordinates2: Optional[list[Coordinate]] = None
    shifts: list[list[int]] | None = None

@router.post("/extract")
async def read_dxf_file(file: UploadFile):
    file_path = "./tmp/" + unique.unique_string(20) + ".dxf"
    with open(file_path, "wb") as F:
        F.write(await file.read())
    coordinates = extract.extract_entities(file_path)
    return {"coordinates": coordinates}

@router.post("/draw")
async def read_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    dicts2 = [item.model_dump() for item in body.coordinates2] if body.coordinates2 else None
    file_path = draw.draw_entities(dicts, entities2=dicts2 if dicts2 else None)
    return FileResponse(file_path)

@router.post("/generate")
async def read_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    file_path = generate.generate_dxf(dicts)
    return FileResponse(file_path)

@router.post("/shift")
async def read_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    dxf_util = dxf.Dxf()
    new_coordinates = dxf_util.shift_measurements(dicts, body.shifts)
    return {"coordinates": new_coordinates}
