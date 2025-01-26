from server import app
from functions import DatabaseOperations

from fastapi import Request

@app.get("/user/check_auth", tags=["users"])
async def check_auth_s(request: Request):
    return await DatabaseOperations.check_auth(request=request)