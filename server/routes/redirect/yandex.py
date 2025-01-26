from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from functions import DatabaseOperations, RandomUtils
from secrets import token_urlsafe
from server import app, database
import httpx


@app.get("/redirect/yandex", response_class=HTMLResponse)
async def redirect_yandex():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Redirect</title>
        <script>
            function getTokenFromUrl() {
                const hash = window.location.hash.substring(1);
                const params = new URLSearchParams(hash);
                return params.get('access_token')
            }
            async function sendToken() {
                const token = getTokenFromUrl();
                if (token) {
                    const response = await fetch('/redirect/yandex2', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ access_token: token }),
                    });
                    const result = await response.json();
                    console.log(result);
                } else {
                    console.error('Токен не найден в URL');
                }
            }
            window.onload = sendToken;
        </script>
    </head>
    <body>
        <h1>Redirecting...</h1>
    </body>
    </html>
    """


@app.post("/redirect/yandex2")
async def redirect_yandex2(request: Request):
    data = await request.json()
    access_token = data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token не предоставлен")

    headers = {
        'Authorization': f'OAuth {access_token}'
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://login.yandex.ru/info", headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())

    user_info = response.json()
    login = user_info.get('login')
    mail = user_info.get('default_email')

    db = database["users"]
    user = await db.find_one({"login": login})
    tokens = {await RandomUtils.generate_random_word(15): token_urlsafe(64) for _ in range(5)}
    response = HTMLResponse(content=f"""
        <html><head><script type="text/javascript">window.location.href = "/"; </script></head>""")
    if user:
        await db.update_one({"login": login}, {"$set": {"tokens": tokens}})
    else:
        await db.insert_one({
            "_id": await DatabaseOperations.get_next_id(db),
            "login": login,
            "tokens": tokens,
            "permissions": {
                "user": True,
                "administrator": False,
                "Developer": False
            },
            "auth_type": "yandex"
        })

    for key, value in tokens.items():
        response.set_cookie(key, value)
    
    response.set_cookie("login", login)
    
    return response
