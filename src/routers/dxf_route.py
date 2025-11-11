from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from utils import unique
from utils.dxf_v1 import extract, draw, generate
from utils.dxf_shift import shift


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


# -------------------------------
# Helper to delete files in background
# -------------------------------
def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)


# -------------------------------
# /extract endpoint
# -------------------------------
@router.post("/extract")
async def read_dxf_file(file: UploadFile):
    os.makedirs("./tmp", exist_ok=True)
    file_path = f"./tmp/{unique.unique_string(20)}.dxf"

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())

        coordinates = extract.extract_entities(file_path)
        return {"success": True, "coordinates": coordinates}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# -------------------------------
# /draw endpoint
# -------------------------------
@router.post("/draw")
async def draw_dxf_file(body: Coordinates, background_tasks: BackgroundTasks):
    os.makedirs("./tmp", exist_ok=True)
    dicts = [item.model_dump() for item in body.coordinates]
    dicts2 = [item.model_dump() for item in body.coordinates2] if body.coordinates2 else None
    file_path = draw.draw_entities(dicts, entities2=dicts2 if dicts2 else None)

    # Schedule file deletion after response
    background_tasks.add_task(remove_file, file_path)
    return FileResponse(file_path)


# -------------------------------
# /generate endpoint
# -------------------------------
@router.post("/generate")
async def generate_dxf_file(body: Coordinates, background_tasks: BackgroundTasks):
    os.makedirs("./tmp", exist_ok=True)
    dicts = [item.model_dump() for item in body.coordinates]
    file_path = generate.generate_dxf(dicts)

    # Schedule file deletion after response
    # background_tasks.add_task(remove_file, file_path)
    return FileResponse(file_path)


# -------------------------------
# /shift endpoint
# -------------------------------
@router.post("/shift")
async def shift_dxf_file(body: Coordinates):
    dicts = [item.model_dump() for item in body.coordinates]
    new_coordinates = shift.shift_dxf(dicts, body.shifts)
    return {"coordinates": new_coordinates}
