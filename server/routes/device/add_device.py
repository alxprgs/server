from server import app, database
from functions import get_next_id

from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv

@app.get("/device/add_device")
async def add_device(device_ip: str, acess_code: int, mac_adress: str):
    load_dotenv()
    acess_code_real = os.getenv("ACESS_CODE")
    if int(acess_code) == int(acess_code_real):
        db = database["devices"]
        try:
            await db.insert_one({
                "_id": await get_next_id(db),
                "device_ip": device_ip,
                "mac_adress": mac_adress
            })
            return JSONResponse({"status": True, "massage": "Успех"}, status_code=200)
        except Exception as e:
            return JSONResponse({"status": False, "massage": f"Внутренная ошибка сервера: {e}"}, status_code=500)
    else:
        return JSONResponse({"status": False, "massage": "Неверный код доступа"}, status_code=400)