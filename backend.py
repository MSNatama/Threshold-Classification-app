from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tensorflow import keras
from starlette.requests import Request
from keras.models import load_model
import cv2
import numpy as np
import logging
import base64

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
model = load_model('modelv2.h5')

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def thresholding(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresholded = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return thresholded

def preprocess_image(img):
    try:
        thrsh = thresholding(img)
        resized = cv2.resize(thrsh, (128, 128))
        normalized = resized / 255.0
        return normalized.reshape(128, 128, 1)
    except Exception as e:
        logging.error(f"Error during preprocessing: {str(e)}")
        raise HTTPException(status_code=400, detail="Error during preprocessing")

class_labels = ["Bacterial leaf Blight", "Brown Spot", "Leaf Smut"]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict/")
async def predict(request: Request, file: UploadFile = File(...)):
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_np is None:
            raise HTTPException(status_code=400, detail="Invalid image")

        preprocessed_image = preprocess_image(img_np)

        prediction = model.predict(preprocessed_image.reshape(1, 128, 128, 1))

        result = np.argmax(prediction, axis=1)

        predicted_class_label = class_labels[result[0]]

        original_image_b64 = base64.b64encode(contents).decode('utf-8')
        thresholded_image_b64 = base64.b64encode(cv2.imencode('.png', thresholding(img_np))[1]).decode('utf-8')

        response_data = {
            "prediction": predicted_class_label,
            "original_image_b64": original_image_b64,
            "thresholded_image_b64": thresholded_image_b64,
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": response_data})

@app.get("/reset/")
async def reset_image(request: Request):
    global uploaded_image_data 
    uploaded_image_data = None  
    return {"message": "Page Reseted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)