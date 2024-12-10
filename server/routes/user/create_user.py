from server import app, database
from functions import create_hash, generate_random_word, create_random
from fastapi.responses import JSONResponse
from secrets import token_urlsafe

@app.get("/user/create_user")
async def create_user(login: str, password: str, mail: str):
    db = database["users"]
    try:
        if await db.find_one({"login": login}):
            return JSONResponse({"status": False, "message": "Пользователь с таким логином уже зарегистрирован."}, status_code=400)

        if await db.find_one({"mail": mail}):
            return JSONResponse({"status": False, "message": "Пользователь с такой почтой уже зарегистрирован."}, status_code=400)

        hashed_password = await create_hash(text=password)
        tokens = {await generate_random_word(15): token_urlsafe(64) for _ in range(5)}

        await db.insert_one({
            "login": login,
            "mail": mail,
            "password": hashed_password,
            "tokens": tokens,
            "permissions": {
                "user": True,
                "administrator": False,
                "Developer": False
            }
        })

        response = JSONResponse({"status": True, "message": "Успешная регистрация."}, status_code=200)
        response.set_cookie("login", login)
        for key, value in tokens.items():
            response.set_cookie(key, value)
        response = await create_random(response=response)
        return response
    except Exception as e:
        return JSONResponse({"status": False, "message": f"error: {e}"}, status_code=500)
