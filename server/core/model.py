import torch
from .logging import logger
from ultralytics import YOLO

def init_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = 'best.pt'
    model = YOLO(model_path).to(device)
    if device.type == "cuda": 
        logger.info(f"Модель инициализирована. Используется видеокарта.") 
    else: 
        logger.info("Модель инициализирована. Используется процессор.")
    return model