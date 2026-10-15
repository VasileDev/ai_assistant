from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from api.questions import router as questions_router
from api.routes import router as documents_router
from services.store import load_store_on_startup

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the saved document index before the API accepts questions.
    load_store_on_startup()
    yield


app = FastAPI(title="AI Assistant", lifespan=lifespan)
app.include_router(documents_router)
app.include_router(questions_router)

if STATIC_DIR.is_dir():
    app.mount("/app", StaticFiles(directory=str(STATIC_DIR), html=True), name="app")
else:
    @app.get("/app", include_in_schema=False)
    @app.get("/app/", include_in_schema=False)
    def frontend_not_installed():
        # Keep the API available while the frontend files are being added.
        raise HTTPException(status_code=503, detail="Web interface is not available.")
