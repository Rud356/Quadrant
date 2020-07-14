import asyncio
import configparser
from os import mkdir
from sys import exit

from motor import motor_asyncio
from quart import Quart

from json_encoder import CustomJSONEncoder

app = Quart(__name__)
app.json_encoder = CustomJSONEncoder
loop = asyncio.get_event_loop()
connected_users = {}


def load_config():
    config = configparser.ConfigParser(allow_no_value=True)
    try:
        with open("./settings.ini") as conf:
            config.read_file(conf)
        return config

    except FileNotFoundError:
        config.add_section("App")
        config.set("App", "debug", "True")
        config.set("App", "allow_reg", "True")
        config.set("App", "upload_folder", "resourses/")
        config.set("App", "# To see more about mongodb connection visit https://docs.mongodb.com/manual/reference/connection-string/", "")
        config.set("App", "db_conn_string", "mongodb://localhost:27017")
        config.set("App", "# TTK means the number of minutes until killing user from cache for inactive", "")
        config.set("App", "TTK", "10")
        config.set("App", "# Next parameter shows how big (in megabytes) can be the uploaded file to server", "")
        config.set("App", "max_payload_size", "20")
        config.set("App", "login_cache_size", "1024")
        config.set("App", "priv_key", "")
        config.set("App", "pub_key", "")
        config.set("App", "ca_certs", "")
        config.set("App", "host", "localhost")
        config.set("App", "port", "8080")

        with open("settings.ini", 'w') as conf:
            config.write(conf)

        print("Change configuration file!")
        exit(1)


config = load_config()

app.config["DEBUG"]: bool = config.getboolean("App", "debug") or False
app.config["ALLOW_REG"]: bool = config.getboolean("App", "allow_reg") or False
app.config['UPLOAD_FOLDER']: str = config.get("App", "upload_folder")
app.config["DB_CONN_STR"]: str = config.get("App", "db_conn_string")
app.config["TTK"]: int = config.getint("App", "TTK")
app.config['MAX_CONTENT_LENGTH']: int = config.getfloat("App", "max_payload_size") * 1024 * 1024 + 1

if config.getfloat("App", "max_payload_size") == float("inf"):
    print("Do not set payload size as inf")
    print("Resetted value to default limit: 20MB")
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1

app.config['LOGIN_CACHE_SIZE']: int = config.getint("App", "login_cache_size")


try:
    mkdir(app.config["UPLOAD_FOLDER"])

except FileExistsError:
    pass

client = motor_asyncio.AsyncIOMotorClient(
    app.config['DB_CONN_STR'],
    io_loop=loop
)

db = client["asyncio_chat"]
if app.config["DEBUG"]:
    db = client["debug_chat"]
