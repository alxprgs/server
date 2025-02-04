from server import app

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

@app.post("/user/leave_user", tags=["users"])
async def leave_user(request: Request, response: Response):
    cookies = request.cookies
    response = RedirectResponse(url='/', status_code=307)
    for cookie_name in cookies.keys():
        response.delete_cookie(key=cookie_name)
    return response
