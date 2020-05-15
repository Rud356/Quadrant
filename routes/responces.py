from quart import Response, request, jsonify


async def error(description: str="Not found", code: int = 404):
    return Response(description, code)


async def warning(description: str):
    return Response(description, 405)


async def success(data: object, code: int = 200):
    return jsonify({"responce": data, "code": code})
