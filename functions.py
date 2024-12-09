import asyncio
import time
from datetime import datetime
import os
import hashlib
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
import secrets

def clear() -> None:
    os.system({"nt": "cls", "posix": "clear"}.get(os.name, "clear"))

async def get_next_id(collection) -> int:
    last_document = await collection.find_one(sort=[("_id", -1)])
    return (last_document.get("_id", 0) + 1) if last_document else 1
    
async def get_unix_timestamp() -> int:
    await asyncio.sleep(0)
    unix_timestamp = int(time.time())
    return unix_timestamp

async def get_formatted_timestamp() -> str:
    await asyncio.sleep(0)
    now = datetime.now()
    formatted_timestamp = now.strftime('%H:%M:%S %d:%m:%Y')
    return formatted_timestamp

async def system_log(t: str) -> None:
    from server import database
    t = str(t)
    db = database["system_logs"]
    formatted_timestamp = await get_formatted_timestamp()
    await db.insert_one({
        "_id": await get_next_id(db),
        "message": t,
        "timestamp": formatted_timestamp
    })

async def visit(request) -> None:
    from server import database
    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    await database["visits"].insert_one({
        "_id": await get_next_id(database["visits"]),
        "url": str(request.url),
        "method": request.method,
        "headers": dict(request.headers),
        "ip": client_ip,
    })

async def create_hash(text) -> str:
    text = str(text)
    text = text + "3886go@fcbE7QukKNxXNWNkxfndsZUxLh9sZjNg82VDWCN_2.se39g4JN*hmieJBg8kkovY_EeyKTi3DDJhaLmJA*pQsQxFP9CynwA3a"
    text_bytes = text.encode("utf-8")
    hashed_text = hashlib.sha256(text_bytes).hexdigest()

    return str(hashed_text)

async def check_auth(request) -> bool:
    from server import database
    token = request.cookies.get('token')
    user = await database["users"].find_one({"token": token})
    if user:
        return True
    else:
        return False

async def check_permissions(request, permission) -> bool:
    from server import database
    auth = await check_auth(request=request)
    if auth:
        token = request.cookies.get('token')
        user = await database["users"].find_one({"token": token})
        try:
            permission = user["permissions"][permission]
            return permission
        except:
            return False
    else:
        return False
    
def check_credentials(credentials: HTTPBasicCredentials):
    load_dotenv()
    correct_username = secrets.compare_digest(credentials.username, os.getenv("DEV_LOGIN"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("DEV_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True