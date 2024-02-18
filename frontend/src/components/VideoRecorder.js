import React, { useState } from 'react';
import { ReactMediaRecorder } from 'react-media-recorder';

export default function VideoRecorder() {
  const [mediaBlobUrl, setMediaBlobUrl] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  const downloadRecordedVideo = () => {
    if (mediaBlobUrl) {
      const a = document.createElement('a');
      a.href = mediaBlobUrl;
      a.download = 'recorded-video.webm';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      
    }
  };

  // Styles for the video and its container
  const videoContainerStyle = {
    display: 'flex',
    flexDirection: 'column', // Stack children vertically
    justifyContent: 'center',
    alignItems: 'center',
    height: '500px', // Set to the desired height
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
      <h1>Hello StackBlitz!</h1>
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
    </div>
  );
}
