from fastapi import APIRouter, UploadFile
from utils import unique
from utils import dxf
from pydantic import BaseModel
from fastapi.responses import FileResponse


router = APIRouter()

class Coordinate(BaseModel):
    entity_type: str
    x: float
    y: float
    z: float

class Coordinates(BaseModel):
    coordinates: list[Coordinate]


@router.post("/parse")
async def read_dxf_file(file: UploadFile):
    file_path = "./tmp/" + unique.unique_string(20) + ".dxf"
    with open(file_path, "wb") as F:
        F.write(await file.read())
    dxf_util = dxf.Dxf(file_path)
    coordinates = dxf_util.extract()   
    return {"coordinates": coordinates}

@router.post("/draw")
async def read_dxf_file(body: Coordinates):
    dxf_util = dxf.Dxf("")
    file_path = dxf_util.draw(body.coordinates)
    return FileResponse(file_path)