import React, { useState } from 'react';
import { ReactMediaRecorder } from 'react-media-recorder';
import ContextChooser from './ContextChooser';
import { useNavigate } from 'react-router-dom';

export default function VideoRecorder({video_context}) {
  const [mediaBlobUrl, setMediaBlobUrl] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [selectedOption, setSelectedOption] = useState('preliminary evaluation');

  let navigate = useNavigate();

  const downloadRecordedVideo = async () => {
    if (mediaBlobUrl) {
      const a = document.createElement('a');
      a.href = mediaBlobUrl;
      a.download = 'recorded-video.webm';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      setTimeout(3000);

      // Call backend
      const response = await fetch('http://127.0.0.1:5000/videoParser', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
      });
  
      const data = await response.json();
  
      if (response.ok) {
        console.log('Success:', data);
        // Handle success
      } else {
        console.error('Error:', data.error);
        // Handle error
      }

      // Redirect to reportpage with context chosen for eval
      navigate(`/report?context=${selectedOption}`);
    }
  };

  // Styles for the video and its container
  const videoContainerStyle = {
    display: 'flex',
    flexDirection: 'column', // Stack children vertically
    justifyContent: 'center',
    alignItems: 'center',
    height: '500px', // Set to the desired height
    width: '600px',
    margin: 'auto', // Center the container on the page
    position: 'relative', // For absolute positioning of child elements
    backgroundColor: 'black',
  };

  const videoStyle = {
    width: '100%', // This makes the video fill the container
    maxHeight: '100%', // Ensures the video does not overflow the container's height
  };

  const buttonContainerStyle = {
    position: 'absolute', // Position buttons at the bottom of the container
    bottom: '0', // Align to the bottom
    width: '100%', // Match the width of the container
    display: 'flex',
    justifyContent: 'center', // Center buttons horizontally
  };

  return (
    <div>
      <div style={videoContainerStyle}>
        <ReactMediaRecorder
          video
          blobPropertyBag={{ type: 'video/webm' }}
          render={({ previewStream, status, startRecording, stopRecording }) => (
            <>
              <p>{status}</p>
              {/* Always present video element but conditionally display the stream */}
              <video
                autoPlay
                playsInline
                muted
                style={{ ...videoStyle, display: isRecording ? 'block' : 'none' }}
                ref={(videoRef) => {
                  if (videoRef && previewStream) {
                    videoRef.srcObject = previewStream;
                  }
                }}
              />
              {!isRecording && <div style={{ width: '100%', height: '100%' }}></div>}
              <div style={buttonContainerStyle}>
                <button 
                  onClick={() => { 
                    startRecording(); 
                    setIsRecording(true); 
                  }}>Start Recording</button>
                <button 
                  onClick={() => { 
                    stopRecording(); 
                    setIsRecording(false); 
                  }}>Stop Recording</button>
                <button
                  disabled={!mediaBlobUrl}
                  onClick={downloadRecordedVideo}
                >
                  Submit
                </button>
              </div>
            </>
          )}
          onStop={(blobUrl) => setMediaBlobUrl(blobUrl)}
        />
      </div>
      <ContextChooser selectedOption={selectedOption} setSelectedOption={setSelectedOption}/>
    </div>
  );
}
