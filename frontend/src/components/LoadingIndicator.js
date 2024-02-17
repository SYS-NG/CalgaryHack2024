import React from 'react';

const loadingStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: '#6A5ACD', // Indigo background, same as the protected page
};

const spinnerStyle = {
  border: '16px solid #f3f3f3', // Light grey border for the spinner
  borderTop: '16px solid #3498db', // Blue color for the spinner top
  borderRadius: '50%',
  width: '120px',
  height: '120px',
  animation: 'spin 2s linear infinite',
};

const LoadingIndicator = () => (
  <div style={loadingStyle}>
    <div style={spinnerStyle}></div>
  </div>
);

export default LoadingIndicator;
