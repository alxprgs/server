from server import app, mongo_db, mongo
from server.core.functions.mongodb import check_permissions, check_connection
from server.core.api.schemes import SetPermissions
from fastapi.responses import JSONResponse
from fastapi import Request, status

@app.post("/user/set_permissions", tags=["users"])
async def set_permissions(data: SetPermissions, request: Request):    
    if await check_connection(mongo=mongo) == False:
        return JSONResponse({"status": False, "message": "Нет подключения к базе данных, действие невозможно."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    has_permission = await check_permissions(request=request, permission="user_edit_permission", database=mongo_db)
    
    if has_permission:
        try:
            result = await mongo_db["users"].find_one_and_update(
                {"login": data.login},
                {"$set": {f"permissions.{data.permission}": data.permission_status}}
            )
            if result:
                return JSONResponse({"status": True, "message": "Разрешение успешно изменено."}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse({"status": False, "message": "Пользователь не найден"}, status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JSONResponse({"status": False, "message": f"Ошибка: {e}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse({"status": False, "message": "Недостаточно прав."}, status_code=status.HTTP_400_BAD_REQUEST)
