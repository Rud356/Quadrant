from os import path


class BaseConfig(object):
    DEBUG: bool = False
    TEST: bool = False
    MONGO_URI: str = "mongodb://mongodb0.example.com:27017"
    UPLOAD_FOLDER: str = path.join("app", "data")
    EXTERNAL_FILES_HOSTING: bool = False
    MAX_CONTENT_LENGTH: int = 20 * 1024 * 1024 + 1
