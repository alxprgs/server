from .functions.hash import create_hash
from .config import settings
from server import logger
from secrets import token_urlsafe

async def setup(db):
    db = db["users"]
    root_login = "root"
    try:
        user = await db.find_one({"login": root_login})
    except Exception as e:
        logger.error("Ошибка при поиске root пользователя: %s", e, exc_info=True)
        return False

    hashed_password = create_hash(settings.ROOTUSER_PASSWORD)
    new_token = token_urlsafe(64)
    permissions = {
        "all": True,
        "user_delete": True,
        "user_edit_permission": True,
        "user_edit_login": True
    }

    if user:
        try:
            await db.update_one(
                {"login": root_login},
                {"$set": {
                    "password": hashed_password,
                    "token": new_token,
                    "permissions": permissions
                }}
            )
            logger.info("Данные root пользователя успешно обновлены.")
            return True
        except Exception as e:
            logger.critical("Ошибка обновления root пользователя: %s", e, exc_info=True)
            return False
    else:
        try:
            await db.insert_one({
                "login": root_login,
                "mail": "root@asfes.ru",
                "password": hashed_password,
                "token": new_token,
                "permissions": permissions
            })
            logger.info("Root пользователь успешно создан.")
            return True
        except Exception as e:
            logger.critical("Ошибка создания root пользователя: %s", e, exc_info=True)
            return False