import time

from fastapi import Request


async def processing_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    process_time = round(time.time() - start_time, 6)
    response.headers["X-Process-Time"] = str(process_time)
    return response
