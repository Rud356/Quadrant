from app import app, loop
from routes import *

app.run(debug=True, loop=loop)