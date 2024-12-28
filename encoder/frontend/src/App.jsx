import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [image, setImage] = useState(null); // State for uploaded image preview
  const [audioPath, setAudioPath] = useState(null); // State for generated audio path
  const [loading, setLoading] = useState(false); // State to show loading status

  // Handle image upload
  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      // Preview the image
      const reader = new FileReader();
      reader.onload = (e) => setImage(e.target.result);
      reader.readAsDataURL(file);

      // Send the image to the backend
      const formData = new FormData();
      formData.append("file", file);

      try {
        setLoading(true); // Start loading
        const response = await axios.post("http://127.0.0.1:8000/encode", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Backend response:", response.data); // Log the backend response
        setAudioPath(response.data.audio_path); // Update audioPath state with backend response
      } catch (error) {
        console.error("Error generating audio:", error);
        alert("Failed to generate audio. Please try again.");
      } finally {
        setLoading(false); // Stop loading
      }
    }
  };

  // Play the audio
  const playAudio = () => {
    if (audioPath) {
      const audio = new Audio(`http://127.0.0.1:8000/${audioPath}`);
      audio.play();
    } else {
      alert("No audio available to play!");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-3xl font-bold text-blue-600 mb-6">SSTV Encoder</h1>

      {/* Image Upload */}
      <label className="btn btn-primary">
        Upload Image
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
      </label>

      {/* Loading Indicator */}
      {loading && <p className="text-blue-500 mt-4">Generating audio...</p>}

      {/* Image Preview */}
      {image && (
        <div className="mt-4 p-4 border rounded shadow bg-white">
          <h2 className="text-lg font-semibold mb-2">Image Preview:</h2>
          <img src={image} alt="Uploaded" className="max-w-full h-auto" />
        </div>
      )}

      {/* Audio Controls */}
      {audioPath && (
        <div className="mt-4">
          <button className="btn btn-accent" onClick={playAudio}>
            Play Generated Audio
          </button>
        </div>
      )}
    </div>
  );
};

export default App;