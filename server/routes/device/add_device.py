from server import app, database, eth_mode
from functions import DatabaseOperations

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import Body

import os
from dotenv import load_dotenv

@app.post("/device/add_device", tags=["device"])
async def add_device(
    device_ip: str = Body(...), 
    acess_code: int = Body(...), 
    mac_adress: str = Body(...)
):
    if not eth_mode:
        return JSONResponse({"status": False, "message": "Отсутствует доступ к базе данных. Взаимодействие невозможно."}, status_code=523)

    load_dotenv()
    acess_code_real = os.getenv("ACESS_CODE")
    
    if int(acess_code) == int(acess_code_real):
        db = database["devices"]
        try:
            await db.insert_one({
                "_id": await DatabaseOperations.get_next_id(db),
                "device_ip": device_ip,
                "mac_adress": mac_adress
            })
            return JSONResponse({"status": True, "message": "Успех"}, status_code=200)
        except Exception as e:
            return JSONResponse({"status": False, "message": f"Внутренняя ошибка сервера: {e}"}, status_code=500)
    else:
        return JSONResponse({"status": False, "message": "Неверный код доступа"}, status_code=400)
