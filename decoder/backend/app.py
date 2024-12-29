from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import os
import soundfile as sf
from PIL import Image
from scipy import signal
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("decoded", exist_ok=True)
app.mount("/decoded", StaticFiles(directory="decoded"), name="decoded")

# SSTV Constants
SAMPLE_RATE = 44100
BLACK_FREQ = 1500
WHITE_FREQ = 2300
SYNC_FREQ = 1200

def find_start(audio_data):
    """Find start of image data by detecting leader tone"""
    window_size = int(0.1 * SAMPLE_RATE)
    for i in range(0, len(audio_data) - window_size, window_size // 2):
        chunk = audio_data[i:i + window_size]
        freqs = np.fft.fftfreq(len(chunk), 1/SAMPLE_RATE)
        fft = np.abs(np.fft.fft(chunk))
        peak_freq = freqs[np.argmax(fft)]
        if abs(peak_freq - 1900) < 100:  # Leader tone found
            return i + window_size
    return 0

def detect_frequency(chunk):
    """More accurate frequency detection using zero-crossing rate and FFT"""
    if len(chunk) < 10:
        return BLACK_FREQ
        
    # Use FFT for frequency detection
    freqs = np.fft.fftfreq(len(chunk), 1/SAMPLE_RATE)
    fft = np.abs(np.fft.fft(chunk))
    
    # Find peaks in the expected frequency range
    valid_range = (freqs >= BLACK_FREQ - 200) & (freqs <= WHITE_FREQ + 200)
    valid_freqs = freqs[valid_range]
    valid_fft = fft[valid_range]
    
    if len(valid_fft) == 0:
        return BLACK_FREQ
        
    peak_idx = np.argmax(valid_fft)
    return valid_freqs[peak_idx]

def decode_line(audio_data, start_idx):
    """Decode one line of image data"""
    pixels = []
    sync_samples = int(0.009 * SAMPLE_RATE)  # 9ms sync
    porch_samples = int(0.003 * SAMPLE_RATE)  # 3ms porch
    pixel_samples = int(0.00144 * SAMPLE_RATE)  # Pixel duration
    
    # Skip sync and porch
    current_idx = start_idx + sync_samples + porch_samples
    
    # Decode pixels
    for _ in range(320):  # Robot 36 width
        if current_idx + pixel_samples > len(audio_data):
            break
            
        chunk = audio_data[current_idx:current_idx + pixel_samples]
        freq = detect_frequency(chunk)
        
        # Convert frequency to pixel value
        pixel_value = np.clip((freq - BLACK_FREQ) / (WHITE_FREQ - BLACK_FREQ) * 255, 0, 255)
        pixels.append(int(pixel_value))
        
        current_idx += pixel_samples
        
    return pixels, current_idx

@app.post("/decode")
async def decode_audio(file: UploadFile = File(...)):
    try:
        print(f"Processing file: {file.filename}")
        
        # Read audio file
        audio_data, sample_rate = sf.read(file.file)
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
            
        # Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Find start of image data
        start_pos = find_start(audio_data)
        print(f"Start position found at sample {start_pos}")
        
        # Initialize image array
        image_data = []
        current_pos = start_pos
        
        # Decode each line
        for _ in range(240):  # Robot 36 height
            if current_pos >= len(audio_data):
                break
                
            line_pixels, current_pos = decode_line(audio_data, current_pos)
            if len(line_pixels) == 320:  # Only add complete lines
                image_data.append(line_pixels)
        
        if not image_data:
            raise ValueError("No valid image data decoded")
            
        # Create image from decoded data
        image_array = np.array(image_data, dtype=np.uint8)
        decoded_image = Image.fromarray(image_array)
        
        # Enhance contrast
        decoded_image = Image.fromarray(
            np.clip((np.array(decoded_image) - 128) * 1.5 + 128, 0, 255).astype(np.uint8)
        )
        
        # Save image
        image_path = f"decoded/{file.filename.split('.')[0]}.png"
        decoded_image.save(image_path)
        print(f"Decoded image saved to {image_path}")
        
        return JSONResponse(content={
            "message": "Audio decoded successfully",
            "image_path": image_path
        })
        
    except Exception as e:
        print("\n=== Decoding Error ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        traceback.print_exc()
        return JSONResponse(
            content={"error": f"Decoding failed: {str(e)}"},
            status_code=500
        )