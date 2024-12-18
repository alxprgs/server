from server import app, templates
from functions import DatabaseOperations

from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse

@app.get("/html/auth", tags=["html"])
async def auth_html(request: Request):
    auth = await DatabaseOperations.check_auth(request=request)
    if auth:
        return RedirectResponse(url="/", status_code=307)
    else:
        return templates.TemplateResponse("auth/auth.html", {"request": request})