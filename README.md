## Automatic Spot Fire Extinguishing System (ASFES)

**Ссылка на репозиторий:** [github.com/alxprgs/server](https://github.com/alxprgs/server)

---

### Описание проекта
ASFES представляет собой модульную и расширяемую систему автоматического обнаружения и тушения очагов возгорания с использованием современных технологий машинного зрения и асинхронного веб-фреймворка FastAPI. Проект нацелен на обеспечение высокую надёжность и безопасность эксплуатации, а также удобство интеграции в существующие инфраструктуры.

### Ключевые возможности
- **Обнаружение очагов возгорания** с помощью модели YOLO (Ultralytics) на базе PyTorch.
- **Асинхронная архитектура** для параллельной обработки запросов и взаимодействия с базами данных (MongoDB, MySQL, Redis).
- **Гибкая система аутентификации и авторизации** пользователей, основанная на токенах и настраиваемых правах доступа.
- **Автоматическая настройка root‑пользователя** при первом запуске сервиса.
- **Документированное API** с поддержкой OpenAPI (Swagger UI).

### Структура репозитория
```
├── Dockerfile
├── LICENSE
├── README.md
├── run.py
├── requirements.txt
├── .env
└── server
    ├── __init__.py
    ├── routes
    │   ├── processing
    │   │   └── find_firev4.py
    │   └── user
    │       ├── auth_user.py
    │       ├── check_auth.py
    │       ├── create_user.py
    │       ├── leave_user.py
    │       ├── set_permission.py
    │       └── user_delete.py
    └── core
        ├── api
        │   └── schemes.py
        ├── config.py
        ├── databases
        │   ├── database_mongo.py
        │   ├── database_mysql.py
        │   └── database_redis.py
        ├── functions
        │   ├── hash.py
        │   ├── mongodb.py
        │   └── time.py
        ├── logging.py
        ├── model.py
        ├── root_user.py
        └── tags_metadata.py
```

### Установка и запуск

#### 1. Настройка окружения
1. Скопируйте файл `.env.example` в `.env` и заполните необходимые переменные окружения:
   ```dotenv
   MONGO_URL=<Ваш MongoDB URI>
   MYSQL_URL=<Ваш MySQL URI>        # необязательно
   REDIS_HOST=<Хост Redis>          # необязательно
   REDIS_PORT=<Порт Redis>         # необязательно
   SERVER_PORT=5005
   ROOTUSER_PASSWORD=<Пароль root>
   ```

#### 2. Установка зависимостей
```bash
pip install --no-cache-dir -r requirements.txt
```

#### 3. Локальный запуск (без Docker)
```bash
python run.py
```
Сервис будет доступен по адресу `http://0.0.0.0:${SERVER_PORT}`.

### Сборка и запуск контейнера Docker

1. **Сборка образа**
```bash
docker build \
  --build-arg SERVER_PORT=$(grep SERVER_PORT .env | cut -d '=' -f2) \
  -t asfes:latest .
```
2. **Запуск контейнера**
```bash
docker run -d \
  -p $(grep SERVER_PORT .env | cut -d '=' -f2):$(grep SERVER_PORT .env | cut -d '=' -f2) \
  --env-file .env \
  --name asfes-server \
  asfes:latest
```

### Использование API
После запуска приложение предоставляет следующие маршруты:

#### Пользователи (`/user`)
- `POST /user/create_user` — регистрация нового пользователя.
- `POST /user/auth_user` — авторизация (установка куки `token`).
- `GET  /user/check_auth` — проверка текущей сессии.
- `POST /user/leave_user` — выход пользователя (удаление куки).
- `POST /user/set_permissions` — изменение прав доступа заданного пользователя (только для администраторов).
- `DELETE /user/del_user` — удаление пользователя (только для администраторов).

#### Обработка изображений (`/processing`)
- `POST /processing/v4/mark_fire` — загрузка изображения, аннотация очагов возгорания и возврат изображения с метками;
  параметр `return_coordinates=true` возвращает JSON с координатами вместо изображения.

Все маршруты документированы и доступны через автоматический интерфейс Swagger UI: `http://loaclhost:${SERVER_PORT}/docs`.

### Лицензия
Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).




