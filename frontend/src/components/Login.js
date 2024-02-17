// src/Login.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../authService';
import { auth } from '../firebase-config';

const formStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  gap: '20px',
  backgroundColor: '#f0f8ff',
};

const formContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%', // Ensure the form container fills its parent
    maxWidth: '400px',
  };
  

const inputStyle = {
  width: '60%',
  padding: '10px',
  margin: '10px 0',
  borderRadius: '5px',
  border: '1px solid #ccc',
};

const buttonStyle = {
  width: '65%',
  padding: '10px 20px',
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
};

const Login = () =>  {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged((user) => {
            if (user) navigate('/protected');
        });
        return unsubscribe; // Cleanup subscription on unmount
    }, [navigate]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            await login(email, password);
        } catch (error) {
            console.error('Failed to login', error);
        }
    };

    return (
        <div style={formStyle}>
            <h2>Login</h2>
            <form onSubmit={handleSubmit} style={formContainerStyle}>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="Email"
                    style={inputStyle}
                />
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Password"
                    style={inputStyle}
                />
                <button type="submit" style={buttonStyle}>Login</button>
            </form>
        </div>
    );
}

export default Login;
