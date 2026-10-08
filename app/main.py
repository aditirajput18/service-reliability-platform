from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers import services


BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Service Reliability Platform",
    description="A lightweight service reliability monitoring platform.",
    version="0.1.0"
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR.parent / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


app.include_router(services.router)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
	request=request,
	name="dashboard.html",
       context={"request": request}
    )


@app.get("/health")
def application_health():
    return {
        "status": "healthy"
    }
