from os import system, name

from app import app, loop
from routes import init_routes

if name == 'nt':
    system("cls")

else:
    system("clear")

init_routes()
app.run(
    'localhost', 80,
    app.config['DEBUG'],
    loop=loop
)