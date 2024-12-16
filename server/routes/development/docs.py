from server import app, security
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from functions import AuthUtils
from fastapi.security import HTTPBasicCredentials
from fastapi import Depends

@app.get("/docs", include_in_schema=False)
async def custom_docs(credentials: HTTPBasicCredentials = Depends(security)):
    AuthUtils.check_credentials(credentials)
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Документация")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc(credentials: HTTPBasicCredentials = Depends(security)):
    AuthUtils.check_credentials(credentials)
    return get_redoc_html(openapi_url="/openapi.json", title="Документация ReDoc")

@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(credentials: HTTPBasicCredentials = Depends(security)):
    AuthUtils.check_credentials(credentials)
    return app.openapi()