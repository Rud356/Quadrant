from .collections import make_index
from app.app import loop

loop.run_until_complete(make_index())
