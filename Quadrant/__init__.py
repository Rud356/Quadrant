import Quadrant.middlewares
import Quadrant.quadrant_logging
from Quadrant.config import quadrant_config
from Quadrant.quadrant_app import app
from Quadrant.resources import (
    user_resources, authorization_resource, media_uploads_resource,
    registration_resource
)

if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass


app.include_router(user_resources.router)
app.include_router(authorization_resource.router)
app.include_router(media_uploads_resource.router)
app.include_router(registration_resource.router)