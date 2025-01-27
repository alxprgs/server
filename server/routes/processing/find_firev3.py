import os
import tempfile
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw
from inference_sdk import InferenceHTTPClient
from dotenv import load_dotenv
from server import app

load_dotenv()

@app.post("/processing/v3/mark_fire", tags=["processing"])
async def mark_firev3(file: UploadFile = File(...)):
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=os.getenv("ROBOFLOW_API")
    )

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        response = CLIENT.infer(temp_file_path, model_id="fire-uzqpo-ekpmw/2")

        original_image = Image.open(temp_file_path)
        image_width, image_height = original_image.size

        predictions = response.get("predictions", [])
        draw = ImageDraw.Draw(original_image)
        for prediction in predictions:
            x = int(prediction["x"])
            y = int(prediction["y"])
            width = int(prediction["width"])
            height = int(prediction["height"])

            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(image_width, x + width)
            y2 = min(image_height, y + height)

            confidence = prediction["confidence"]
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            draw.text((x1, y1), f"{prediction['class']} {confidence:.2f}", fill="red")
    

        output_image_path = "output_image.jpg"
        original_image.save(output_image_path)

        return FileResponse(output_image_path, media_type='image/jpeg')

    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
