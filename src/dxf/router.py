from fastapi import APIRouter, UploadFile
from utils import unique
from utils import dxf
from pydantic import BaseModel
from fastapi.responses import FileResponse


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
    shifts: list[list[int]] | None = None

@router.post("/parse")
async def read_dxf_file(file: UploadFile):
    file_path = "./tmp/" + unique.unique_string(20) + ".dxf"
    with open(file_path, "wb") as F:
        F.write(await file.read())
    dxf_util = dxf.Dxf()
    coordinates = dxf_util.extract_entities(file_path)
    return {"coordinates": coordinates}

@router.post("/draw")
async def read_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    dxf_util = dxf.Dxf()
    file_path = dxf_util.draw_entities(dicts)
    return FileResponse(file_path)

@router.post("/shift")
async def read_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    # shifts = [item.model_dump() for item in body.shifts]
    dxf_util = dxf.Dxf()
    new_coordinates = dxf_util.shift_measurements(dicts, body.shifts)
    return {"coordinates": new_coordinates}
