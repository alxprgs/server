from server import app, mongo_db, mongo
from server.core.functions.mongodb import check_permissions, check_connection
from server.core.api.schemes import DelUser

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


@app.delete("/user/del_user", tags=["users"])
async def del_user(data: DelUser, request: Request):
    if await check_connection(mongo=mongo) == False:
        return JSONResponse({"status": False, "message": "Нет подключения к базе данных, действие невозможно."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    admin = await check_permissions(request=request, permission="user_delete", database=mongo_db)
    if not admin:
        raise HTTPException(detail="Недостаточно прав.", status_code=status.HTTP_403_FORBIDDEN)
    
    try:
        result = await mongo_db["users"].find_one_and_delete({"login": data.login})
        if result:
            return JSONResponse({"status": True, "message": "Пользователь успешно удалён."}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse({"status": False, "message": "Пользователь не найден."}, status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse({"status": False, "message": f"server error: {e}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
