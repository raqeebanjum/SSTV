import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [audio, setAudio] = useState(null); // State for uploaded audio
  const [imagePath, setImagePath] = useState(null); // State for decoded image path

  // Handle audio file upload
  const handleAudioUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("file", file);
  
      try {
        const response = await axios.post("http://127.0.0.1:8000/decode", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        console.log("Backend response:", response.data); // Log response from backend
        setDecodedImage(response.data.image_path);
      } catch (error) {
        console.error("Error decoding audio:", error);
        alert("Failed to decode audio. Please try again.");
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold text-blue-600 mb-6">SSTV Decoder</h1>

      {/* Audio File Upload */}
      <label className="btn btn-primary">
        Upload Audio
        <input
          type="file"
          accept="audio/*"
          onChange={handleAudioUpload}
          className="hidden"
        />
      </label>

      {/* Display Decoded Image */}
      {imagePath && (
        <div className="mt-4 p-4 border rounded shadow bg-white">
          <h2 className="text-lg font-semibold mb-2">Decoded Image:</h2>
          <img src={`http://127.0.0.1:8000/${imagePath}`} alt="Decoded" className="max-w-full h-auto" />
        </div>
      )}
    </div>
  );
};

export default App;