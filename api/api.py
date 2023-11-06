from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi_pagination import add_pagination
import json

def create_app() -> FastAPI:
    app = FastAPI(
        title="DM Driver",
        description="DM Driver",
        version="1.0",
        generate_unique_id_function=custom_id_fn,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["main"])
    async def health() -> str:
        return "ok"
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
    

    # from api.routers import organisations, rosters, shifts, tags, users, workers
    # from api.routes import tags_router
    # app.include_router(users.auth_router)
    # app.include_router(organisations.router)
    # app.include_router(rosters.router)
    # app.include_router(workers.router)
    # app.include_router(shifts.router)
    # app.include_router(users.query_router)
    # app.include_router(tags_router)

    add_pagination(app)

    @app.get("/endpoints", tags=["main"])
    async def endpoints() -> str:
        url_list = [{"path": route.path, "name": route.name} for route in app.routes]
        return json.dumps(url_list)
    
    return app


def custom_id_fn(route: APIRoute) -> str:
    return f"{route.name}"  # f"{route.tags[0]}-{route.name}"