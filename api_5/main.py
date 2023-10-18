from fastapi import FastAPI, File, UploadFile, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import aiofiles
import uvicorn
from typing import List

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
from time import time
from deepface import DeepFace

import scr.mesonet
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
import tensorflow as tf

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from secrets import token_urlsafe

import requests
import json


# Instantiate a MesoNet model with pretrained weights
meso = scr.mesonet.Meso4()
meso.load('./weights/Meso4_DF')

app = FastAPI()

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    'http://127.0.0.1:5500/index_2upload.html'
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Authentication
security = HTTPBearer()

TOKEN_EXPIRATION_MINUTES = 10

def generate_token() -> str:
    expiration = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    token = token_urlsafe(32) + expiration.isoformat()
    return token

def authenticate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Validate the token against your authentication logic
    if not validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return True

def validate_token(token: str) -> bool:
    expiration = token[-25:]
    expiration_time = datetime.fromisoformat(expiration)
    return datetime.utcnow() < expiration_time

def change_name(path, image_name, mill, i):
    last = ['id_front', 'id_back', 'face']
    fr = 'png' if image_name.split('.')[1] == 'png' else 'jpg'
    dst = f'{path}/{mill}_{last[i]}.{fr}'
    os.rename(f'{path}/{image_name}', dst)
    return dst

# BUTTON: set param ID user, WEBSITE LAYER1
@app.get('/{id}')
async def kyc(id: str, request: Request, response: Response):
    print('Process 1 ID:',id)
    response = templates.TemplateResponse("kyc.html", {"request": request})
    response.set_cookie(key="id", value=str(id))  # Set the "name" cookie
    return response

# revice card image, Face iamge, API LAYER2
@app.post("/uploads-verify/{id}", status_code=201)
async def verification_face_and_id_card(id: str, files: List[UploadFile] = File(...)):
    print('Process 2 ID:',id)
    folder = 'face-id'
    mill = int(time() * 1000)
    img_veri = []

    for i, file in enumerate(files):
        destination_file_path = folder + '/' + file.filename  # output file path
        async with aiofiles.open(destination_file_path, 'wb') as out_file:
            while content := await file.read(1024):  # async read file chunk
                await out_file.write(content)  # async write file chunk

        n_img = change_name(folder, file.filename, mill, i)
        img_veri.append(n_img)

    print('IMAGE INPUT',img_veri)

    
    # 0: Deepfake, 1: Real
    img = load_img(img_veri[2], target_size=(256, 256))
    img_array = img_to_array(img)
    img_array /= 255.0
    img_array = tf.expand_dims(img_array, 0)
    deepfake_status = 'Pass' if round(meso.predict(img_array)[0][0]) ==1 else 'No pass' 
    print('DEEPFAKE DETECTED',deepfake_status)

    faceMatch_status = 'No pass'
    if (deepfake_status == 'Pass'):
        # face mathcing layer
        status = DeepFace.verify(img1_path=img_veri[0], img2_path=img_veri[2], model_name="Facenet512")
        output = {"status": "OK", 'verify': bool(status['verified']), "filenames": [file.filename for file in files]}
        if ( bool(status['verified'])):
            faceMatch_status = 'Pass'

    print('FACE MATCHING', faceMatch_status)

    # TODO _____ 
    # Update database from URL upage db to url/id , send status_db
    # Define the API endpoint URL
    url = 'http://localhost:5000/database'  # Replace with the appropriate URL
    data = {
        'id': id,
        'status': json.dumps({'Deepfake': deepfake_status, 'faceMatching': faceMatch_status})
    }
    image1_path = img_veri[0] 
    image2_path = img_veri[2] 
    with open(image1_path, 'rb') as image1_file, open(image2_path, 'rb') as image2_file:
        # Set the files for the request
        files = {
            'image1': (image1_path, image1_file),
            'image2': (image2_path, image2_file)
        }
        requests.post(url, data=data, files=files)
    return 


if __name__ == '__main__':
    token = generate_token()
    print("Generated Token:", token)
    uvicorn.run(app, host='127.0.0.1', port=8080)
    print("running")
