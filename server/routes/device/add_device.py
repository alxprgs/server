from server import app, database, eth_mode
from functions import DatabaseOperations

from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

@app.get("/device/add_device")
async def add_device(device_ip: str, acess_code: int, mac_adress: str):
    if eth_mode == False:
        return JSONResponse({"status": False, "message": "Отсутсвует доступ к базе данных. Взаимодействие невозможно."}, status_code=523)
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
            return JSONResponse({"status": True, "massage": "Успех"}, status_code=200)
        except Exception as e:
            return JSONResponse({"status": False, "massage": f"Внутренная ошибка сервера: {e}"}, status_code=500)
    else:
        return JSONResponse({"status": False, "massage": "Неверный код доступа"}, status_code=400)