from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

import Quadrant.config as config
from Quadrant.models import db_init

app = FastAPI(
    debug=config.quadrant_config.debug_mode.value,
    title="Quadrant API",
    description="Chat API that is meant to be easy",
    version="0.0.1",
    openapi_url="/api/v1/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("shutdown")
def shutdown_event():
    db_init.Session.close_all()
