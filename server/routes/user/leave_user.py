from server import app
from fastapi import Request, Response
from fastapi.responses import JSONResponse

@app.get("/user/leave_user")
async def leave_user(request: Request, response: Response):
    cookies = request.cookies
    response = JSONResponse({"status": True, "message": "Выход с аккаунта."})
    for cookie_name in cookies.keys():
        response.delete_cookie(key=cookie_name)
    return response
