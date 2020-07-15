from os import system, name

from app import app, loop, load_config
from routes import init_routes


if name == 'nt':
    system("cls")

else:
    system("clear")


config = load_config()

init_routes()
app.run(
    config.get("App", 'host'), config.getint("App", 'port'),
    app.config['DEBUG'],
    loop=loop,
    ca_certs=config.get("App", "ca_certs") or None,
    certfile=config.get("App", "pub_key") or None,
    keyfile=config.get("App", "priv_key") or None
)
