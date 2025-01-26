from server import app, database
from functions import DatabaseOperations

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.delete("/user/del_user", tags=["users"])
async def del_user(username: str, request: Request):
    admin = await DatabaseOperations.check_permissions(request=request, permission="administrator")
    if not admin:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        result = await database["users"].find_one_and_delete({"login": username})
        if result:
            return JSONResponse({"status": True, "message": "Пользователь успешно удалён."}, status_code=200)
        else:
            return JSONResponse({"status": False, "message": "Пользователь не найден."}, status_code=404)
    except Exception as e:
        return JSONResponse({"status": False, "message": f"server error: {e}"}, status_code=500)
