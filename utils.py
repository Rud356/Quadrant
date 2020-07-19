import configparser
from sys import exit
from typing import Any, List


def exclude_keys(dictionary: dict, exclude_keys: List[Any]):
    for key in exclude_keys:
        dictionary.pop(key, None)


def string_strips(string: str) -> str:
    return string.strip(' ').strip("\n").strip("\t")


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
        config.set(
            "App",
            "# To see more about mongodb connection visit https://docs.mongodb.com/manual/reference/connection-string/",
            ""
        )
        config.set("App", "db_conn_string", "mongodb://localhost:27017")
        config.set(
            "App",
            "# TTK means the number of minutes until killing user from cache for inactive",
            ""
        )
        config.set("App", "TTK", "10")
        config.set(
            "App",
            "# Next parameter shows how big (in megabytes) can be the uploaded file to server",
            ""
        )
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
