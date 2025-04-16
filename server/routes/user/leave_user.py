from server import app

from fastapi import status
from fastapi.responses import JSONResponse


@app.post("/user/leave_user", tags=["users"])
async def leave_user():
    response = JSONResponse({"status": True}, status_code=status.HTTP_200_OK)
    response.delete_cookie(key="token")
    response.delete_cookie(key="login")
    return response
