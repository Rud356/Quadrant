from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse

import Quadrant.config as config

app = FastAPI(
    debug=config.quadrant_config.debug_mode.value,
    title="Quadrant API",
    description="Chat API that is meant to be easy",
    version="0.0.1",
    openapi_url="/api/v1/openapi.json",
    default_response_class=ORJSONResponse,
)
