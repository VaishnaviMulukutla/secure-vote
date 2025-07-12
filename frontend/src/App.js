import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [voterId, setVoterId] = useState('');
  const [message, setMessage] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (showCamera) {
      navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            console.log("📷 Camera started");
          }
        })
        .catch((err) => {
          console.error("🚫 Camera error:", err);
          setMessage("Camera access denied.");
        });
    }
  }, [showCamera]);

  const checkVoterId = async () => {
    setMessage('Checking Voter ID...');
    try {
      const res = await fetch('http://localhost:5000/check_id', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voter_id: voterId }),
      });
      const data = await res.json();
      setMessage(data.message);
      if (data.valid) setShowCamera(true);
    } catch (err) {
      console.error("❌ check_id error", err);
      setMessage('Failed to check ID.');
    }
  };

  const captureAndVerify = async () => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) {
        setMessage("Failed to capture image.");
        return;
      }

      const formData = new FormData();
      formData.append('voter_id', voterId);
      formData.append('photo', blob, `${voterId}_capture.jpg`);

      try {
        const res = await fetch('http://localhost:5000/verify_face', {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        setMessage(data.message);
      } catch (err) {
        console.error("❌ verify_face error", err);
        setMessage('Failed to verify face.');
      }
    }, 'image/jpeg');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-bold mb-4">🗳️ E-Voting System</h1>

      <input
        type="text"
        placeholder="Enter Voter ID"
        value={voterId}
        onChange={(e) => setVoterId(e.target.value)}
        className="border p-2 rounded w-64 mb-4"
      />
      <button
        onClick={checkVoterId}
        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
      >
        Check ID
      </button>

      <p className="mt-4 text-center text-sm text-gray-700">{message}</p>

      {showCamera && (
        <div className="mt-6 text-center">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-80 rounded shadow-md mb-4"
          />
          <canvas ref={canvasRef} className="hidden" />
          <br />
          <button
            onClick={captureAndVerify}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
          >
            Capture & Verify Face
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
