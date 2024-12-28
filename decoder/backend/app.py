from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import numpy as np
import scipy.io.wavfile as wavfile
from PIL import Image

app = FastAPI()

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a directory exists to save temporary files
os.makedirs("uploaded", exist_ok=True)
os.makedirs("decoded", exist_ok=True)

# Mount the 'decoded' directory to serve output images
app.mount("/decoded", StaticFiles(directory="decoded"), name="decoded")

@app.post("/decode")
async def decode_audio(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}")  # Log file name

        # Save the uploaded file locally
        file_path = f"uploaded/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        print(f"File saved to {file_path}")

        # Load the WAV file
        sample_rate, audio_signal = wavfile.read(file_path)
        print(f"Audio loaded: Sample rate = {sample_rate}, Length = {len(audio_signal)}")

        # Placeholder: Generate dummy image
        image_array = np.random.randint(0, 255, (240, 320), dtype=np.uint8)
        image = Image.fromarray(image_array)
        decoded_image_path = f"decoded/{file.filename.split('.')[0]}.png"
        image.save(decoded_image_path)
        print(f"Decoded image saved to {decoded_image_path}")

        # Return the file path for the decoded image
        return JSONResponse(content={"message": "Audio decoded successfully", "image_path": decoded_image_path})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)