from server import app, templates
from functions import DatabaseOperations

from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse

@app.get("/", tags=["html"])
async def root_html(request: Request):
    auth = await DatabaseOperations.check_auth(request=request)
    if auth:
        return templates.TemplateResponse("root/root.html", {"request": request})
    else:
        return RedirectResponse(url="/html/auth", status_code=307)