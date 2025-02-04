from server import app, database, eth_mode
from functions import DatabaseOperations

from fastapi.responses import JSONResponse
from fastapi import HTTPException

import os
import re
from dotenv import load_dotenv
import logging

def is_valid_ip(ip: str) -> bool:
    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    return ip_pattern.match(ip) is not None

def is_valid_mac(mac: str) -> bool:
    mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return mac_pattern.match(mac) is not None

@app.post("/device/add_device", tags=["device"], response_class=JSONResponse)
async def add_device(device_ip: str, acess_code: int, mac_adress: str):
    if not eth_mode:
        raise HTTPException(status_code=523, detail="Отсутствует доступ к базе данных. Взаимодействие невозможно.")

    load_dotenv()
    acess_code_real = os.getenv("ACESS_CODE")
    
    if acess_code_real is None:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера: отсутствует код доступа.")

    if not is_valid_ip(device_ip):
        raise HTTPException(status_code=400, detail="Некорректный IP-адрес.")

    if not is_valid_mac(mac_adress):
        raise HTTPException(status_code=400, detail="Некорректный MAC-адрес.")

    if int(acess_code) != int(acess_code_real):
        raise HTTPException(status_code=400, detail="Неверный код доступа.")

    db = database["devices"]
    try:
        await db.insert_one({
            "_id": await DatabaseOperations.get_next_id(db),
            "device_ip": device_ip,
            "mac_adress": mac_adress
        })
        return JSONResponse({"status": True, "message": "Успех"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")