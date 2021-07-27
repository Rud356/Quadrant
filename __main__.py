import uvicorn
from Quadrant import app
from Quadrant.config import quadrant_config

# For debug purpose only
uvicorn.run(
    app,
    debug=quadrant_config.debug_mode.value,
    host="0.0.0.0", port=8000
)