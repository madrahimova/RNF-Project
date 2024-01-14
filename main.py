import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api import app

main = FastAPI()
main.mount("/api", app)


@main.get("/", response_class=HTMLResponse)
async def root():
    return "OK"

if __name__ == "__main__":
    uvicorn.run(main, host="0.0.0.0", port=8000)
