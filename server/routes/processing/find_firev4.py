import cv2
import numpy as np
import math
from fastapi import HTTPException, Response, status, UploadFile, File, Query
from server import app, model, logger

async def process_image_async(image: np.ndarray):
    try:
        results = model(image)
        return results
    except Exception as e:
        logger.error("Ошибка предсказания модели: %s",e)
        raise HTTPException(detail="Ошибка предсказания модели", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def draw_annotations(image: np.ndarray, results) -> tuple:
    height, width = image.shape[:2]
    image_center = (width // 2, height // 2)
    coordinates = []

    cv2.circle(image, image_center, 15, (255, 0, 0), 2)
    cv2.line(image, 
            (image_center[0]-25, image_center[1]), 
            (image_center[0]+25, image_center[1]), 
            (255, 0, 0), 2)
    cv2.line(image, 
            (image_center[0], image_center[1]-25), 
            (image_center[0], image_center[1]+25), 
            (255, 0, 0), 2)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            w = x2 - x1
            h = y2 - y1
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            cv2.line(image, image_center, (center_x, center_y), (0, 0, 255), 2)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            dx = center_x - image_center[0]
            dy = image_center[1] - center_y
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            angle_deg = angle_deg if angle_deg >= 0 else 360 + angle_deg
            
            coordinates.append({
                "x": center_x,
                "y": center_y,
                "angle": round(angle_deg, 2),
                "width": w,
                "height": h
            })

    return image, coordinates

@app.post("/processing/v4/mark_fire/image", tags=["processing"])
async def mark_firev4_image(file: UploadFile = File(...), return_coordinates: bool = Query(default=False)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный формат файла")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(detail="Ошибка чтения изображения", status_code=status.HTTP_400_BAD_REQUEST)

        results = await process_image_async(image)
        
        processed_image, coordinates = draw_annotations(image, results)

        _, encoded_img = cv2.imencode('.jpg', processed_image)
        bytes_image = encoded_img.tobytes()

        if return_coordinates:
            return {
                "coordinates": coordinates
            }
        return Response(content=bytes_image, media_type="image/jpeg")

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.critical("Критическая ошибка: %s", e)
        raise HTTPException(detail="Внутренняя ошибка обработки", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)