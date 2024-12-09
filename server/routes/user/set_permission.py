from server import app, database
from functions import check_permissions
from fastapi import Request
from fastapi.responses import JSONResponse

@app.get("/user/set_permissions")
async def set_permissions(request: Request, permission: str, permission_status: bool, login: str):
    has_permission = await check_permissions(request=request, permission="administrator")
    if has_permission:
        try:
            await database["users"].find_one_and_update(
                {"login": login},
                {"$set": {f"permissions.{permission}": permission_status}}
            )
            return {"status": True, "message": "Permissions updated successfully"}
        except Exception as e:
            return JSONResponse({"status": False, "message": f"error: {e}"})
    else:
        return JSONResponse({"status": False, "message": "Insufficient permissions"})
