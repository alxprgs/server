from server import app
from functions import check_auth

from fastapi import Request

@app.get("/user/check_auth")
async def check_auth_s(request: Request):
    return await check_auth(request=request)
