from fastapi import UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
import torch
from io import BytesIO
from server import app, model

@app.post("/processing/find_Fire")
async def find_Fire(file: UploadFile = File(...), mode: int = 1):
    if mode not in [1, 2]:
        return JSONResponse(content={"status": False, "message": "Неверный тип ответа. (1/2)"}, status_code=400)

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        return JSONResponse(content={"status": False, "message": "Не удалось декодировать изображение."}, status_code=400)

    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0 
    image_tensor = image_tensor.unsqueeze(0)

    if torch.cuda.is_available():
        image_tensor = image_tensor.cuda() 

    if mode == 1:
        h, w, _ = image.shape
        sector_height = h // 9
        sector_width = w // 9

        output_image = image.copy()
        for i in range(1, 9):
            cv2.line(output_image, (0, i * sector_height), (w, i * sector_height), (0, 255, 0), 2)
            cv2.line(output_image, (i * sector_width, 0), (i * sector_width, h), (0, 255, 0), 2)

        _, encoded_image = cv2.imencode('.png', output_image)
        
        image_stream = BytesIO(encoded_image.tobytes())
        image_stream.seek(0)

        safe_filename = f"{file.filename.rsplit('.', 1)[0]}_processed.png".encode('utf-8').decode('latin-1', 'ignore')
        
        return StreamingResponse(image_stream, media_type="image/png", headers={"Content-Disposition": f"attachment; filename={safe_filename}"})

    elif mode == 2:
        with torch.no_grad():
            results = model(image_tensor)

        detected_lights = []

        if hasattr(results, 'xyxy') and len(results.xyxy) > 0:
            for *box, conf in results.xyxy[0]:
                x1, y1, x2, y2 = map(int, box)
                detected_lights.append({
                    "coordinates": [x1.item(), y1.item(), x2.item(), y2.item()],
                    "confidence": float(conf)
                })
        
        return JSONResponse({
            "filename": file.filename,
            "detected_lights": detected_lights
        })

    return JSONResponse(content={"status": False, "message": "Неизвестный режим."}, status_code=400)