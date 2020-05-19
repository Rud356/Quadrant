from os import system
from app import app, loop
from routes import *

system('cls')
app.run(debug=True, loop=loop)