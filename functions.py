import os
import time
import json
import hashlib
import random
import string
import asyncio
from datetime import datetime

from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
import psutil
import secrets
from secrets import token_urlsafe
import aiofiles

load_dotenv()

class Setup:
    async def root_user():
        from server import database as db
        db = db["users"]
        password = await HashUtils.create_hash(str(os.getenv("DEV_PASSWORD")))
        login = str(os.getenv("DEV_LOGIN"))
        tokens = {await RandomUtils.generate_random_word(15): token_urlsafe(64) for _ in range(5)}
        user = await db.find_one({"login": os.getenv("DEV_LOGIN")})
        if user:
            pass
        else:
            await db.insert_one({
                "_id": await DatabaseOperations.get_next_id(db),
                "login": login,
                "mail": None,
                "password": password,
                "tokens": tokens,
                "permissions": {
                    "user": True,
                    "administrator": True,
                    "Developer": True
                },
                "auth_type": "system"
            })

class SystemUtils:
    @staticmethod
    def clear() -> None:
        os.system({"nt": "cls", "posix": "clear"}.get(os.name, "clear"))

class DatabaseOperations:
    async def get_next_id(collection) -> int:
        last_document = await collection.find_one(sort=[("_id", -1)])
        return (last_document.get("_id", 0) + 1) if last_document else 1

    async def system_log(t: str) -> None:
        from server import database
        t = str(t)
        db = database["system_logs"]
        formatted_timestamp = await TimestampUtils.get_formatted_timestamp()
        await db.insert_one({
            "_id": await DatabaseOperations.get_next_id(db),
            "message": t,
            "timestamp": formatted_timestamp
        })

    async def visit(request) -> None:
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        from server import database
        await database["visits"].insert_one({
            "_id": await DatabaseOperations.get_next_id(database["visits"]),
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
            "ip": client_ip,
        })

    async def check_auth(request) -> bool:
        from server import database
        login = request.cookies.get('login')
        if not login:
            return False
        user = await database["users"].find_one({"login": login})
        if not user:
            return False
        tokens = user.get("tokens", {})
        if not tokens:
            return False
        for token_key, token_value in tokens.items():
            cookie_value = request.cookies.get(token_key)
            if cookie_value != token_value:
                return False
        return True

    async def check_permissions( request, permission) -> bool:
        from server import database
        auth = await DatabaseOperations.check_auth(request=request)
        if auth:
            token = request.cookies.get('token')
            user = await database["users"].find_one({"token": token})
            try:
                permission = user["permissions"][permission]
                return permission
            except KeyError:
                return False
        else:
            return False

class AuthUtils:
    @staticmethod
    def check_credentials(credentials: HTTPBasicCredentials):
        correct_username = secrets.compare_digest(credentials.username, str(os.getenv("DEV_LOGIN")))
        correct_password = secrets.compare_digest(credentials.password, str(os.getenv("DEV_PASSWORD")))
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Basic"},
            )
        return True

class RandomUtils:
    @staticmethod
    async def generate_random_word(length: int) -> str:
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    @staticmethod
    async def create_random(response, count: int = 20):
        for _ in range(count):
            key = await RandomUtils.generate_random_word(length=15)
            value = token_urlsafe(64)
            response.set_cookie(key=key, value=value)
        return response

class SystemMetrics:
    @staticmethod
    async def get_cpu_load() -> int:
        return psutil.cpu_percent(interval=1)

    @staticmethod
    async def get_ram_load() -> int:
        return psutil.virtual_memory().percent
    
class TimestampUtils:
    @staticmethod
    async def get_unix_timestamp() -> int:
        await asyncio.sleep(0)
        return int(time.time())

    @staticmethod
    async def get_formatted_timestamp() -> str:
        await asyncio.sleep(0)
        now = datetime.now()
        return now.strftime('%H:%M:%S %d:%m:%Y')

class HashUtils:
    @staticmethod
    async def create_hash(text) -> str:
        text = str(text)
        text += "3886go@fcbE7QukKNxXNWNkxfndsZUxLh9sZjNg82VDWCN_2.se39g4JN*hmieJBg8kkovY_EeyKTi3DDJhaLmJA*pQsQxFP9CynwA3a"
        text_bytes = text.encode("utf-8")
        return hashlib.sha256(text_bytes).hexdigest()

class JsonOperations:
    async def write_to_json(file_name, variable_path, value):
        data = {}
        if os.path.exists(file_name):
            async with aiofiles.open(file_name, 'r') as f:
                content = await f.read()
                if content:
                    data = json.loads(content)
        
        keys = variable_path.split('.')
        current_data = data
        for key in keys[:-1]:
            current_data = current_data.setdefault(key, {})
        current_data[keys[-1]] = value
    
        async with aiofiles.open(file_name, 'w') as f:
            await f.write(json.dumps(data, indent=4))

    async def read_from_json(file_name, variable_path):
        if not os.path.exists(file_name):
            return None
        
        async with aiofiles.open(file_name, 'r') as f:
            content = await f.read()
            if not content:
                return None
            data = json.loads(content)
        
        keys = variable_path.split('.')
        current_data = data
        for key in keys:
            if key in current_data:
                current_data = current_data[key]
            else:
                return None
        return current_data
   