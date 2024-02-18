import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Signup from './components/Signup';
import Main from './components/Main';
import ProtectedPage from './components/ProtectedPage';
import UserProfile from './components/UserProfile';
import LoadingIndicator from './components/LoadingIndicator';
import { auth } from './firebase-config';
import './App.css';
import Signout from './components/Signout';
import ReportPage from './components/ReportPage';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true); // New state to track loading

  useEffect(() => {
    return auth.onAuthStateChanged((user) => {
      setIsAuthenticated(!!user);
      setLoading(false); // Set loading to false once auth state is confirmed
    });
  }, []);

if (loading) {
  return <LoadingIndicator />; // or any loading indicator you prefer
}

    // useEffect(() => {
    //     auth.onAuthStateChanged((user) => {
    //         setIsAuthenticated(!!user);
    //     });
    // }, []);

    return (
        <Router>
            <Routes>
                <Route path="/" element={isAuthenticated ? <Navigate replace to="/protected" /> : <Main />} />
                <Route path="/login" element={isAuthenticated ? <Navigate replace to="/protected" /> : <Login />} />
                <Route path="/signup" element={isAuthenticated ? <Navigate replace to="/protected" /> : <Signup />} />
                <Route path="/protected" element={isAuthenticated ? <ProtectedPage /> : <Navigate replace to="/login" />} />
                <Route path="/user-profile" element={isAuthenticated ? <UserProfile /> : <Navigate replace to="/login" />} />
                <Route path="/logout" element={<Signout/>} />
                <Route path="/report" element={isAuthenticated ? <ReportPage/> : <Navigate replace to="/login" />} />
            </Routes>
        </Router>
    );
}

export default App;
