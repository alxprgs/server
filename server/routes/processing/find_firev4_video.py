import io
import cv2
import numpy as np
import math
from fastapi import WebSocket, WebSocketDisconnect, Query, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from server import model, logger, app

async def process_frame_async(frame: np.ndarray):
    try:
        results = model(frame)
        return results
    except Exception as e:
        logger.error("Ошибка предсказания модели: %s", e)
        raise HTTPException(detail="Ошибка предсказания модели", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def draw_annotations(frame: np.ndarray, results) -> tuple:
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)
    coordinates = []

    cv2.circle(frame, center, 15, (255, 0, 0), 2)
    cv2.line(frame, (center[0] - 25, center[1]), (center[0] + 25, center[1]), (255, 0, 0), 2)
    cv2.line(frame, (center[0], center[1] - 25), (center[0], center[1] + 25), (255, 0, 0), 2)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            w, h = x2 - x1, y2 - y1
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.line(frame, center, (cx, cy), (0, 0, 255), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            dx, dy = cx - center[0], center[1] - cy
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            if angle_deg < 0:
                angle_deg += 360

            coordinates.append({
                "x": cx,
                "y": cy,
                "angle": round(angle_deg, 2),
                "width": w,
                "height": h
            })

    return frame, coordinates

@app.websocket("/processing/v4/mark_fire/video/ws")
async def mark_firev4_video_websocket(
    websocket: WebSocket,
    mode: str = Query(default="annotations", description="Режим работы: 'annotations' или 'coordinates'")
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                await websocket.send_json({"error": "Не удалось декодировать кадр"})
                continue

            results = await process_frame_async(frame)
            annotated_frame, coords = draw_annotations(frame, results)

            if mode == "annotations":
                _, encoded = cv2.imencode('.jpg', annotated_frame)
                await websocket.send_bytes(encoded.tobytes())
            else:
                await websocket.send_json({"coordinates": coords})

    except WebSocketDisconnect:
        logger.info("WebSocket отключён клиентом")
    except Exception as e:
        logger.critical("Критическая ошибка в WebSocket: %s", e)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@app.post("/processing/v4/mark_fire/video", tags=["processing"])
async def mark_firev4_video(
    image: UploadFile = File(..., description="JPEG-изображение кадра"),
    mode: str = Query(default="annotations", description="Режим работы: 'annotations' или 'coordinates'")
):
    data = await image.read()
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось декодировать изображение")

    results = await process_frame_async(frame)
    annotated_frame, coords = draw_annotations(frame, results)

    if mode == "annotations":
        _, encoded = cv2.imencode('.jpg', annotated_frame)
        return StreamingResponse(io.BytesIO(encoded.tobytes()), media_type="image/jpeg")
    else:
        return {"coordinates": coords}
