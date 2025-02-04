from server import app, templates
from fastapi import Request, HTTPException

@app.exception_handler(404)
async def error404(request: Request, exc: HTTPException):
    return templates.TemplateResponse("error/404.html", {"request": request}, status_code=404)