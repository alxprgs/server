from server import app
from functions import create_hash
from fastapi.responses import JSONResponse
from secrets import token_urlsafe

@app.get("/user/create_user")
async def create_user(login, password, mail):
    from server import database
    db = database["users"]
    try:
        user = await db.find_one({"login": login})
        if user:
            return JSONResponse({"status": False, "message": f"Пользаватель с таким логином уже зарегитрирован."})
        else:
            try:
                user = await db.find_one({"mail": mail})
                if user:
                    return JSONResponse({"status": False, "message": f"Пользаватель с такой почтой уже зарегитрирован."})
                else:
                    token = token_urlsafe(256)
                    password = await create_hash(text=password)
                    try:
                        await db.insert_one({
                            "login": login,
                            "mail": mail,
                            "password": password,
                            "token": token,
                            "permissions": {
                                "user": True,
                                "administrator": False,
                                "Developer": False
                            }
                        })
                        response = JSONResponse({"status": True, "message": f"Успешная регистрация."})
                        response.set_cookie(key="token", value=token)
                        return response
                    except Exception as e:
                        return JSONResponse({"status": False, "message": f"error: {e}"})
            except Exception as e:
                return JSONResponse({"status": False, "message": f"error: {e}"})
    except Exception as e:
        return JSONResponse({"status": False, "message": f"error: {e}"})
