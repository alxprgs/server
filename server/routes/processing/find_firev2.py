from fastapi import UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
import cv2
import numpy as np
import torch
from io import BytesIO
from server import app, model
from functions import TimestampUtils

if torch.cuda.is_available():
    model.cuda()

@app.post("/processing/v2/mark_fire", tags=["processing"])
async def mark_fire(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        return JSONResponse(content={"status": False, "message": "Не удалось декодировать изображение."}, status_code=400)

    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0 
    image_tensor = image_tensor.unsqueeze(0)

    if torch.cuda.is_available():
        image_tensor = image_tensor.cuda() 

    with torch.no_grad(), torch.amp.autocast('cuda'):
        results = model(image_tensor)

    output_image = image.copy()

    if hasattr(results, 'xyxy') and len(results.xyxy[0]) > 0:
        for *box, conf in results.xyxy[0]:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    _, encoded_image = cv2.imencode('.png', output_image)
    
    image_stream = BytesIO(encoded_image.tobytes())
    image_stream.seek(0)

    safe_filename = f"{await TimestampUtils.get_unix_timestamp()}_marked.png".encode('utf-8').decode('latin-1', 'ignore')
    
    return StreamingResponse(image_stream, media_type="image/png", headers={"Content-Disposition": f"attachment; filename={safe_filename}"})
