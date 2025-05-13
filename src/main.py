from fastapi import FastAPI

from dxf import router as dxf_router

app = FastAPI()
app.include_router(dxf_router.router, prefix="/api/dxf")

@app.get("/")
async def root():
    return {"message": "welcome!"}