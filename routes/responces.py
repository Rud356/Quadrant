from quart import jsonify


def error(description: str = "Not found", code: int = 404):
    responce = jsonify(description=description)
    responce.status_code = code
    return responce


def warning(description: str):
    responce = jsonify(warning=description)
    responce.status_code = 405
    return responce


def success(data: object, code: int = 200):
    responce = jsonify(response=data, status_code=code)
    responce.status_code = code
    return responce
