from server import app
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi import Request, Response
import os
from secrets import token_urlsafe

load_dotenv()

@app.get("/redirect/vk", tags=["redirect"], response_class=RedirectResponse)
async def redirect_vk(request: Request, response: Response):
    domain = request.headers.get("host")
    link = f"https://id.vk.com/authorize?response_type=code&client_id={os.getenv('client_id')}&redirect_uri={domain}/redirect/vk2&state={token_urlsafe(32)}&code_challenge_method=S256"
    response = RedirectResponse(link)
    return response

@app.post("/redirect/vk2", tags=["redirect"])
async def redirect_vk2():
    pass