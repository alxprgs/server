from server import app, eth_mode
from functions import DatabaseOperations
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from dotenv import load_dotenv
import os

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

@app.post("/smm/send_mail", tags=["smm"], response_class=JSONResponse)
async def send_mail(request: Request, mail: str, text: str, title: str):
    if not eth_mode:
        return JSONResponse({"status": False, "message": "Отсутсвует доступ к базе данных. Взаимодействие невозможно."}, status_code=523)
    
    permission = await DatabaseOperations.check_permissions(request=request, permission="administrator")

    if not permission:
        raise HTTPException(status_code=403, detail="Отказано в доступе.")

    results = []
    try:
        email_list = mail.split(",")

        for email in email_list:
            msg = MIMEMultipart()
            msg['From'] = os.getenv("MAIL_LOGIN")
            msg['To'] = email.strip()
            msg['Subject'] = title
            msg.attach(MIMEText(text, 'plain'))

            await aiosmtplib.send(
                msg,
                hostname='smtp.mail.ru',
                port=465,
                username=os.getenv("MAIL_LOGIN"),
                password=os.getenv("MAIL_PASSWORD"),
                use_tls=True
            )
            results.append({"email": email.strip(), "status": "sent"})

        return JSONResponse({"status": True, "message": "Успех.", "results": results}, status_code=200)

    except Exception as e:
        return JSONResponse({"status": False, "message": f"Ошибка сервера: {e}"}, status_code=500)
