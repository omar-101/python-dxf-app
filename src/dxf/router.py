from fastapi import APIRouter,File, UploadFile
from utils import unique
from utils import dxf


router = APIRouter()


@router.post("/")
async def read_dxf_file(file: UploadFile):
    file_path = "./tmp/" + unique.unique_string(20) + ".dxf"
    with open(file_path, "wb") as F:
        F.write(await file.read())
    dxf_util = dxf.Dxf(file_path)
    dxf_util.extract()      
    dxf_util.draw()  
    return {"filename": file_path}