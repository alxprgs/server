import logging
from datetime import datetime
import colorlog

log_format = "%(log_color)s%(levelname)s:%(reset)s     %(message)s"

current_date = datetime.now().strftime("%d-%m-%y")
start_time = datetime.now().strftime("%H-%M-%S") 

console_handler = colorlog.StreamHandler()
console_handler.setFormatter(colorlog.ColoredFormatter(log_format))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.INFO)