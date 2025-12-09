from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

from utils import unique
from utils.dxf_v1 import extract, draw, generate, merge_cor, cal_length, convert, markar
import importlib
import json

os.environ["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "true"


router = APIRouter()
TMP_DIR = "./tmp"


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
    shifts: Optional[list[list[int]]] = None
    show_length: Optional[bool] = None


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
    # Ensure temporary folder exists
    os.makedirs("./tmp", exist_ok=True)

    # Convert required coordinates to dicts
    coords1 = [c.model_dump() for c in body.coordinates]

    # Convert optional coordinates2 if it exists
    coords2 = [c.model_dump() for c in body.coordinates2] if body.coordinates2 else None

    # Optional shifts and show_length are already in correct format
    shifts = body.shifts

    # show_length
    show_length = body.show_length

    if show_length or shifts:
        coords1 = cal_length.add_length_layer_with_shifts_note(coords1, shifts)
        coords1 = markar.gas_sink_marker(coords1) if show_length else coords1

    # Call the drawing function
    file_path = draw.draw_entities(
        entities=(
            merge_cor.merge_entities_with_dashed(coords1, coords2, type="draw")
            if coords2
            else coords1
        )
    )

    # Schedule file deletion after response
    background_tasks.add_task(remove_file, file_path)

    # Return file directly
    return FileResponse(file_path)


# -------------------------------
# /generate endpoint
# -------------------------------
@router.post("/generate")
async def generate_dxf_file(body: Coordinates, background_tasks: BackgroundTasks):
    os.makedirs("./tmp", exist_ok=True)

    # Convert required coordinates to dicts
    coords1 = [c.model_dump() for c in body.coordinates]

    # Convert optional coordinates2 if it exists
    coords2 = [c.model_dump() for c in body.coordinates2] if body.coordinates2 else None

    # Optional shifts and show_length are already in correct format
    shifts = body.shifts

    # show_length
    show_length = body.show_length

    if show_length or shifts:
        coords1 = cal_length.add_length_layer_with_shifts_note(coords1, shifts)
        coords1 = markar.gas_sink_marker(coords1) if show_length else coords1

    file_path = generate.generate_dxf(
        entities=(
            merge_cor.merge_entities_with_dashed(coords1, coords2, type="dxf")
            if coords2
            else coords1
        )
    )

    # Schedule file deletion after response
    background_tasks.add_task(remove_file, file_path)
    return FileResponse(file_path)


# -------------------------------
# /shift endpoint
# -------------------------------
@router.post("/shift")
async def shift_dxf_file(body: Coordinates):
    module_name = "scripts.shift_script.shift"
    shift_module = importlib.import_module(module_name)
    dicts = [item.model_dump() for item in body.coordinates]
    new_coordinates = shift_module.main(dicts, body.shifts)
    return {"coordinates": new_coordinates}


# -------------------------------
# /convert-dwg endpoint
# -------------------------------
@router.post("/convert-dwg")
async def convert_to_dwg(body: Coordinates, background_tasks: BackgroundTasks):
    # -------------------------------
    # Prepare coordinates
    # -------------------------------
    coords1 = [c.model_dump() for c in body.coordinates]
    coords2 = [c.model_dump() for c in body.coordinates2] if body.coordinates2 else None
    shifts = body.shifts
    show_length = body.show_length

    if show_length or shifts:
        coords1 = cal_length.add_length_layer_with_shifts_note(coords1, shifts)

    # -------------------------------
    # 1) Generate DXF
    # -------------------------------
    dxf_path = generate.generate_dxf(
        entities=(
            merge_cor.merge_entities_with_dashed(coords1, coords2)
            if coords2
            else coords1
        )
    )

    # -------------------------------
    # 2) Convert DXF → DWG
    # -------------------------------
    dwg_path = convert.convert_dxf_to_dwg(dxf_path, output_dir="/tmp")

    # -------------------------------
    # 3) Cleanup temp files
    # -------------------------------
    # background_tasks.add_task(remove_file, dxf_path)
    # background_tasks.add_task(remove_file, dwg_path)

    return FileResponse(
        dwg_path, media_type="application/acad", filename="converted.dwg"
    )
