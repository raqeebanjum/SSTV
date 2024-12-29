from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import scipy.io.wavfile as wavfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("generated", exist_ok=True)
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# SSTV Constants
SAMPLE_RATE = 44100
VIS_CODE = 0x08  # Robot 36
BLACK_FREQ = 1500
WHITE_FREQ = 2300
SYNC_FREQ = 1200

def generate_header():
    """Generate SSTV header (leader tone + VIS)"""
    # 300ms leader tone (1900 Hz)
    t_leader = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), endpoint=False)
    leader = np.sin(2 * np.pi * 1900 * t_leader)
    return leader

def generate_sync():
    """Generate sync pulse"""
    t_sync = np.linspace(0, 0.009, int(SAMPLE_RATE * 0.009), endpoint=False)
    return np.sin(2 * np.pi * SYNC_FREQ * t_sync)

def generate_pixel_tone(intensity):
    """Generate tone for a single pixel"""
    frequency = BLACK_FREQ + (WHITE_FREQ - BLACK_FREQ) * (intensity / 255.0)
    t = np.linspace(0, 0.00144, int(SAMPLE_RATE * 0.00144), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

@app.post("/encode")
async def encode_image(file: UploadFile = File(...)):
    try:
        print(f"Processing file: {file.filename}")
        
        # Read and preprocess image
        image = Image.open(file.file)
        image = image.convert("L")  # Convert to grayscale
        image = image.resize((320, 240))  # Robot 36 resolution
        image_array = np.array(image)
        
        # Normalize image
        image_array = np.clip(image_array, 0, 255)
        
        print("Image preprocessed successfully")
        
        # Generate audio signal
        audio_signal = []
        
        # Add header
        audio_signal.extend(generate_header())
        
        # Process each line
        for row in image_array:
            # Add sync pulse
            audio_signal.extend(generate_sync())
            
            # Add porch (black level reference)
            t_porch = np.linspace(0, 0.003, int(SAMPLE_RATE * 0.003), endpoint=False)
            porch = np.sin(2 * np.pi * BLACK_FREQ * t_porch)
            audio_signal.extend(porch)
            
            # Add pixel data
            for pixel in row:
                audio_signal.extend(generate_pixel_tone(pixel))
        
        # Convert to numpy array and normalize
        audio_signal = np.array(audio_signal)
        audio_signal = audio_signal * 0.9  # Prevent clipping
        
        # Save as WAV file
        wav_path = f"generated/{file.filename.split('.')[0]}.wav"
        wavfile.write(wav_path, SAMPLE_RATE, (audio_signal * 32767).astype(np.int16))
        
        print(f"Audio saved to {wav_path}")
        
        return JSONResponse(content={
            "message": "Audio generated successfully",
            "audio_path": wav_path
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )