from server import app, database, eth_mode
from functions import DatabaseOperations

from fastapi import Request
from fastapi.responses import JSONResponse

@app.get("/user/set_permissions")
async def set_permissions(request: Request, permission: str, permission_status: bool, login: str):
    if eth_mode == False:
        return JSONResponse({"status": False, "message": "Отсутсвует доступ к базе данных. Взаимодействие невозможно."}, status_code=523)
    has_permission = await DatabaseOperations.check_permissions(request=request, permission="administrator")
    if has_permission:
        try:
            await database["users"].find_one_and_update(
                {"login": login},
                {"$set": {f"permissions.{permission}": permission_status}}
            )
            return JSONResponse({"status": True, "message": "Permissions updated successfully"}, status_code=200)
        except Exception as e:
            return JSONResponse({"status": False, "message": f"error: {e}"}, status_code=500)
    else:
        return JSONResponse({"status": False, "message": "Insufficient permissions"}, status_code=400)
