from fastapi import FastAPI

from routers import dxf_route

app = FastAPI()
app.include_router(dxf_route.router, prefix="/api/dxf")


@app.get("/")
async def root():
    return {"message": "i would like to sing you a song"}
