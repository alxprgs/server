from server import app
from fastapi import Request
from functions import check_auth
@app.get("/user/check_auth")
async def check_auth_s(request: Request):
    return await check_auth(request=request)
