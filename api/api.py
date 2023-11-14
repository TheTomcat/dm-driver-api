from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi_pagination import add_pagination

from core.broadcast import broadcast


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broadcast.connect()
    yield
    await broadcast.disconnect()


def create_app() -> FastAPI:
    app = FastAPI(
        title="DM Driver",
        description="DM Driver",
        version="1.0",
        generate_unique_id_function=custom_id_fn,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # @app.get("/health", tags=["main"])
    # async def health() -> str:
    #     return "ok"
    # start debug
    # import debugpy

    # # avoid error in case debugpy is already listening
    # try:
    #     debugpy.listen(("0.0.0.0", 5678))
    # except RuntimeError:
    #     pass
    # debugpy.wait_for_client()
    # breakpoint()
    # # stop debug
    # return "ok"

    from api.routers import (
        combat,
        entity,
        image,
        message,
        participant,
        session,
        tag,
        ws,
    )

    @app.get("/health", tags=["main"])
    async def health() -> str:
        return "ok"

    @app.get("/endpoints", tags=["main"])
    async def endpoints() -> list:
        url_list = [
            {
                "path": route.path if hasattr(route, "path") else None,  # type: ignore
                "name": route.name if hasattr(route, "name") else None,  # type: ignore
                "methods": route.methods if hasattr(route, "methods") else None,  # type: ignore
            }  # type: ignore
            for route in app.routes
        ]
        return url_list

    app.include_router(entity.router)
    app.include_router(participant.router)
    app.include_router(combat.router)
    app.include_router(session.router)
    app.include_router(message.router)
    app.include_router(image.router)
    app.include_router(tag.router)
    app.include_router(ws.router)

    add_pagination(app)
    return app


def custom_id_fn(route: APIRoute) -> str:
    return f"{route.name}"  # f"{route.tags[0]}-{route.name}"
