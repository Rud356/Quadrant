import Quadrant.middlewares
import Quadrant.quadrant_logging
from Quadrant.config import quadrant_config
from Quadrant.quadrant_app import app
from Quadrant.resources import (
    user_resources, authorization_resource, media_uploads_resource,
    registration_resource, relationship_resource, session_resource,
    users_profile
)

if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass


app.include_router(user_resources.router)
app.include_router(authorization_resource.router)
app.include_router(media_uploads_resource.router)
app.include_router(registration_resource.router)
app.include_router(relationship_resource.router)
app.include_router(session_resource.router)
app.include_router(users_profile.router)
