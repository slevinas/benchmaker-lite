import uvicorn
from fastapi import FastAPI

from .routes import router
from .instrumentation import init_instrumentation


def create_app() -> FastAPI:
    app = FastAPI(title="benchmaker-lite API")

    # Init OpenTelemetry
    init_instrumentation(app)

    # Health endpoint
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Vector endpoints
    app.include_router(router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
