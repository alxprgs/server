import os
import tempfile
from pathlib import Path
from fastapi import UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, ImageDraw, ImageOps
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from server import app

load_dotenv()

# Создаем папку для сохранения обработанных изображений, если она не существует
output_folder = Path("output_images")
output_folder.mkdir(exist_ok=True)

@app.post("/processing/v3/mark_fire", tags=["processing"])
async def mark_firev3(
    file: UploadFile = File(...),
    return_coordinates: bool = Query(default=False)
):
    api_key = os.getenv("ROBOFLOW_API")
    if not api_key:
        raise HTTPException(status_code=500, detail="ROBOFLOW_API key is missing in environment variables.")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        CLIENT = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        response = CLIENT.infer(temp_file_path, model_id="fire-uzqpo-ekpmw/2")
        predictions = response.get("predictions", [])

        original_image = Image.open(temp_file_path)
        original_image = ImageOps.exif_transpose(original_image)
        image_width, image_height = original_image.size

        if return_coordinates:
            detections = []
            for prediction in predictions:
                x = int(prediction["x"])
                y = int(prediction["y"])
                width = int(prediction["width"])
                height = int(prediction["height"])
                confidence = prediction["confidence"]
                class_name = prediction["class"]

                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                })

            return JSONResponse(content={
                "image_width": image_width,
                "image_height": image_height,
                "detections": detections
            })

        draw = ImageDraw.Draw(original_image)
        for prediction in predictions:

            x = int(prediction["x"])
            y = int(prediction["y"])
            width = int(prediction["width"])
            height = int(prediction["height"])

            if width <= 0 or height <= 0:
                continue

            x1 = max(0, x - width // 2)
            y1 = max(0, y - height // 2)
            x2 = min(image_width, x + width // 2)
            y2 = min(image_height, y + height // 2)

            if x1 >= x2 or y1 >= y2:
                continue

            confidence = prediction["confidence"]
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            draw.text((x1, y1), f"{prediction['class']} {confidence:.2f}", fill="red")

        output_image_path = output_folder / f"output_image_{os.getpid()}.jpg"
        original_image.save(output_image_path, format="JPEG")

        return FileResponse(output_image_path, media_type='image/jpeg')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)