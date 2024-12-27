import React, { useState } from "react";

const App = () => {
  const [image, setImage] = useState(null); // State for uploaded image
  const [audio, setAudio] = useState(null); // State for generated audio

  // Handle image upload and trigger audio generation
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImage(e.target.result);
        generateAudio(e.target.result); // Trigger audio generation
      };
      reader.readAsDataURL(file);
    }
  };

  // Placeholder for audio generation
  const generateAudio = (imageData) => {
    console.log("Generating audio for image:", imageData); // Debug log
    alert("Audio generation started!"); // Temporary placeholder
    setAudio(new Audio("path-to-generated-audio.wav")); // Replace with real audio generation
  };

  // Play the generated audio
  const playAudio = () => {
    if (audio) {
      audio.play();
    } else {
      alert("No audio generated yet!");
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

      {/* Image Preview */}
      {image && (
        <div className="mt-4 p-4 border rounded shadow bg-white">
          <h2 className="text-lg font-semibold mb-2">Image Preview:</h2>
          <img src={image} alt="Uploaded" className="max-w-full h-auto" />
        </div>
      )}

      {/* Audio Controls */}
      <div className="mt-4">
        <button className="btn btn-accent" onClick={playAudio}>
          Play Audio
        </button>
      </div>
    </div>
  );
};

export default App;