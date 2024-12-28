from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import os
import soundfile as sf
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a directory exists to save decoded files
os.makedirs("decoded", exist_ok=True)

# Serve the 'decoded' directory at '/decoded'
app.mount("/decoded", StaticFiles(directory="decoded"), name="decoded")

# Custom Encoding Constants
SAMPLE_RATE = 44100
FREQS_FOR_NOTES = [500, 600, 700, 800, 900]  # Intro frequencies
NOTE_DURATION = 0.5  # Duration of each intro note
PIXEL_DURATION = 0.001  # Duration for each pixel frequency
BASE_PIXEL_FREQ = 1000  # Base frequency for pixel encoding
PIXEL_STEP = 2  # Frequency step per intensity value


def decode_audio_to_image(audio_data):
    """
    Decode a custom-encoded audio signal back into an image.
    """
    # Step 1: Extract the intro notes
    intro_note_samples = int(NOTE_DURATION * SAMPLE_RATE)
    start = 0
    for expected_freq in FREQS_FOR_NOTES:
        tone = audio_data[start : start + intro_note_samples]
        detected_freq = detect_frequency(tone)
        if abs(detected_freq - expected_freq) > 5:  # Small tolerance for noise
            raise ValueError(f"Intro note mismatch: expected {expected_freq} Hz, got {detected_freq} Hz")
        start += intro_note_samples

    print("Intro notes verified.")

    # Step 2: Decode the pixel frequencies
    pixel_samples = int(PIXEL_DURATION * SAMPLE_RATE)
    pixel_values = []
    while start + pixel_samples <= len(audio_data):
        tone = audio_data[start : start + pixel_samples]
        detected_freq = detect_frequency(tone)
        if detected_freq is None:
            break
        pixel_intensity = int((detected_freq - BASE_PIXEL_FREQ) / PIXEL_STEP)
        pixel_values.append(pixel_intensity)
        start += pixel_samples

    # Step 3: Reconstruct the image
    image_width = 320
    image_height = len(pixel_values) // image_width
    pixel_array = np.array(pixel_values[: image_width * image_height]).reshape((image_height, image_width))
    return pixel_array.astype(np.uint8)


def detect_frequency(signal):
    """
    Detect the dominant frequency in a signal.
    """
    fft = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1 / SAMPLE_RATE)
    dominant_freq = freqs[np.argmax(np.abs(fft))]
    return dominant_freq if dominant_freq > 0 else None


@app.post("/decode")
async def decode_audio(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}")  # Log file name

        # Step 1: Read the uploaded audio file
        audio_data, sample_rate = sf.read(file.file)
        if sample_rate != SAMPLE_RATE:
            return JSONResponse(content={"error": "Incorrect sample rate"}, status_code=400)
        print("Audio file successfully read.")

        # Step 2: Decode the audio into an image
        pixel_array = decode_audio_to_image(audio_data)
        print("Audio decoded into an image.")

        # Step 3: Save the reconstructed image
        decoded_image = Image.fromarray(pixel_array)
        image_path = f"decoded/{file.filename.split('.')[0]}.png"
        decoded_image.save(image_path)
        print(f"Decoded image saved at {image_path}.")

        # Return the path to the decoded image
        return JSONResponse(content={"message": "Audio decoded", "image_path": image_path})

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return JSONResponse(content={"error": str(e)}, status_code=500)