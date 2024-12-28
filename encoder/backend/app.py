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
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a directory exists to save generated files
os.makedirs("generated", exist_ok=True)

# Serve the 'generated' directory at '/generated'
app.mount("/generated", StaticFiles(directory="generated"), name="generated")

# Custom Encoding Constants
SAMPLE_RATE = 44100
FREQS_FOR_NOTES = [500, 600, 700, 800, 900]  # Five frequencies for the intro notes
NOTE_DURATION = 0.5  # Duration of each note in seconds


def generate_custom_audio(image_array):
    """
    Generate a custom-encoded audio signal.
    """
    audio_signal = []

    # Step 1: Add five half-second notes at the beginning
    for freq in FREQS_FOR_NOTES:
        audio_signal.extend(generate_tone(freq, NOTE_DURATION))

    # Step 2: Encode the image data (map pixel intensity within valid frequency range)
    for line in image_array:
        for pixel in line:
            freq = 1000 + int(pixel) * 2  # Scale pixel value to avoid exceeding frequency range
            audio_signal.extend(generate_tone(freq, 0.001))  # Short duration per pixel

    return np.array(audio_signal)


def generate_tone(freq, duration):
    """
    Generate a sine wave tone for a given frequency and duration.
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)


@app.post("/encode")
async def encode_image(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}")  # Log file name

        # Step 1: Read and resize the uploaded image
        image = Image.open(file.file)
        print("Image successfully opened.")
        image = image.resize((320, 240))  # Custom resolution
        print("Image resized to 320x240.")

        # Step 2: Convert image to grayscale (intensity encoding)
        image_array = np.array(image.convert("L"))
        print("Image converted to grayscale.")

        # Step 3: Generate custom audio
        audio_signal = generate_custom_audio(image_array)
        print("Custom audio signal generated.")

        # Step 4: Save the audio as a WAV file
        wav_path = f"generated/{file.filename.split('.')[0]}.wav"
        wavfile.write(wav_path, SAMPLE_RATE, (audio_signal * 32767).astype(np.int16))
        print(f"Audio file saved at {wav_path}.")

        # Return the file path for playback
        return JSONResponse(content={"message": "Audio generated", "audio_path": wav_path})

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return JSONResponse(content={"error": str(e)}, status_code=500)