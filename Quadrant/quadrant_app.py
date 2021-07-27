from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.openapi.utils import get_openapi

import Quadrant.config as config
from Quadrant.models import db_init

app = FastAPI(
    debug=config.quadrant_config.debug_mode.value,
    openapi_url="/api/v1/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("shutdown")
def shutdown_event():
    db_init.Session.close_all()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Quadrant API",
        description="Chat API that is meant to be easy",
        version="0.0.1",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
