import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [audio, setAudio] = useState(null); // State for uploaded audio
  const [decodedImage, setDecodedImage] = useState(null); // State for the decoded image

  // Handle audio upload and decoding
  const handleAudioUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setAudio(file);

      // Send the audio to the backend
      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await axios.post("http://127.0.0.1:8000/decode", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Backend response:", response.data); // Log backend response
        setDecodedImage(`http://127.0.0.1:8000/${response.data.image_path}`); // Set the decoded image URL
      } catch (error) {
        console.error("Error decoding audio:", error);
        alert("Failed to decode audio. Please try again.");
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold text-blue-600 mb-6">SSTV Decoder</h1>

      {/* Audio Upload */}
      <label className="btn btn-primary">
        Upload Audio
        <input
          type="file"
          accept="audio/*"
          onChange={handleAudioUpload}
          className="hidden"
        />
      </label>

      {/* Decoded Image Preview */}
      {decodedImage && (
        <div className="mt-4 p-4 border rounded shadow bg-white">
          <h2 className="text-lg font-semibold mb-2">Decoded Image:</h2>
          <img src={decodedImage} alt="Decoded" className="max-w-full h-auto" />
        </div>
      )}
    </div>
  );
};

export default App;