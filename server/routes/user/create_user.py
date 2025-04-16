from server import app, mongo_db, mongo
from secrets import token_urlsafe
from server.core.functions.hash import create_hash
from server.core.functions.time import token_expiration_time
from server.core.functions.mongodb import check_connection
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from server.core.api.schemes import CreateUser

@app.post("/user/create_user", tags=["users"])
async def create_user(data: CreateUser):
    if await check_connection(mongo=mongo) == False:
        return JSONResponse({"status": False, "message": "Нет подключения к базе данных, действие невозможно."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    db = mongo_db["users"]
    try:
        existing_user = await db.find_one({"$or": [{"login": data.login}, {"mail": data.mail}]})
        if existing_user:
            field = "логином" if existing_user.get("login") == data.login else "почтой"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Пользователь с таким {field} уже зарегистрирован.")
        token_expiration = token_expiration_time
        hashed_password = create_hash(text=data.password)
        token = token_urlsafe(96)

        user_data = {
            "login": data.login,
            "mail": data.mail,
            "password": hashed_password,
            "token": token,
            "token_expiration": token_expiration,
            "permissions": {
                "user": True,
                "administrator": False,
                "developer": False
            },
        }

        await db.insert_one(user_data)
        response = JSONResponse({"status": True, "message": "Успешная регистрация."},status_code=status.HTTP_201_CREATED)
        response.set_cookie(key="token",value=token,secure=True,httponly=True,samesite='Lax')
        return response

    except Exception as e:
        raise HTTPException(detail=f"Ошибка сервера: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)