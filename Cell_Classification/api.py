# api.py

import uvicorn
from fastapi import FastAPI, HTTPException
import datetime
import time
from src.models.model import predict
from loguru import logger
from pydantic import BaseModel
from typing import List
from src.utils import load_sample, save_image_as_tif
import numpy as np
import os

HOST = "0.0.0.0"
PORT = 9090

# Define the request and response schemas
class CellClassificationPredictRequestDto(BaseModel):
    cell: str  # Base64 encoded image string

class CellClassificationPredictResponseDto(BaseModel):
    is_homogenous: int

app = FastAPI()
start_time = time.time()

@app.get('/api')
def hello():    
    uptime = str(datetime.timedelta(seconds=int(time.time() - start_time)))
    return {
        "service": "cell-segmentation-usecase",
        "uptime": uptime
    }

@app.get('/')
def index():
    return {"message": "Your endpoint is running!"}

@app.post('/predict', response_model=CellClassificationPredictResponseDto)
def predict_endpoint(request: CellClassificationPredictRequestDto):
    try:
        # Decode and load the image
        sample = load_sample(request.cell)
        image = sample.get("image")
        
        if image is None:
            raise ValueError("Image decoding failed.")

        # Ensure the image is in the correct format 
        if not isinstance(image, np.ndarray):
            raise TypeError("Decoded image is not a NumPy array.")
        
        # Save the image as a 16-bit .tif file
        save_path = os.path.join("data/saved_images", f"image_{int(time.time())}.tif")
        save_image_as_tif(image, save_path)
        logger.info(f"Image saved at {save_path}")

        # Make prediction by passing the image array
        predicted_homogenous_state = predict(image)
        
        # Return the prediction
        response = CellClassificationPredictResponseDto(
            is_homogenous=predicted_homogenous_state
        )
        
        return response

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(
        'api:app',
        host=HOST,
        port=PORT,
        reload=True  # Enable auto-reload for development; disable in production
    )
