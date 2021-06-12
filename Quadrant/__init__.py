import Quadrant.middlewares
import Quadrant.quadrant_logging
from Quadrant.config import quadrant_config

from Quadrant.resources import user_resources

if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass


if __name__ == "__main__":
    from Quadrant.quadrant_app import app
    app.include_router(user_resources.router)
