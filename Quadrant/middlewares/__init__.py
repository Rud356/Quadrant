from fastapi.middleware import Middleware
from starlette_csrf import CSRFMiddleware

from Quadrant.config import quadrant_config
from Quadrant.middlewares.authorization import user_authorization
from Quadrant.middlewares.processing_time import processing_time
from Quadrant.middlewares.sqlalchemy_session import get_sqlalchemy_session
from Quadrant.quadrant_app import app

# TODO: work with CORS
app.add_middleware(CSRFMiddleware, secret=quadrant_config.Security.csrf_secret.value)
app.middleware("http")(processing_time)
app.middleware("http")(get_sqlalchemy_session)
app.middleware("http")(user_authorization)
