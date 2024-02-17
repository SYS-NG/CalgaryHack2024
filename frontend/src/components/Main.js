// src/Main.js
import React from 'react';
import { Link } from 'react-router-dom';

const mainStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: '#48D1CC', // A vibrant teal background
  color: '#FFFFFF', // White text for contrast
  gap: '20px',
};

const buttonStyle = {
  padding: '10px 20px',
  backgroundColor: '#FFD700', // A vibrant gold color
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  fontSize: '18px', // Larger font size for readability
};

const Main = () =>  {
  return (
    <div style={mainStyle}>
      <h1>Welcome to Our App</h1>
      <Link to="/login"><button style={buttonStyle}>Login</button></Link>
      <Link to="/signup"><button style={buttonStyle}>Signup</button></Link>
    </div>
  );
}

export default Main;
