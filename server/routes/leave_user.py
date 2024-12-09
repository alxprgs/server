from server import app
from fastapi.responses import JSONResponse

@app.get("/user/leave_user")
async def leave_user():
    response = JSONResponse({"status": True, "message": "Выход с аккаунта."})
    response.delete_cookie(key="token")
    return response
