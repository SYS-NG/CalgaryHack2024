import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../authService';
import { auth } from '../firebase-config';
import LoadingIndicator from './LoadingIndicator';
import { db } from '../firebase-config';
import { doc, getDoc } from "firebase/firestore"; 
import VideoRecorder from './VideoRecorder';

const protectedStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: '#6A5ACD', // A vibrant indigo background
  color: '#FFFFFF', // White text for contrast
  gap: '20px',
};

const buttonStyle = {
  padding: '10px 20px',
  backgroundColor: '#FF6347', // A vibrant tomato color
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  fontSize: '18px', // Larger font size for readability
};

const ProtectedPage = () => {
    let navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchUserData = async () => {
          const user = auth.currentUser;
          console.log(user)
          if (user) {
            const userRef = doc(db, "users", user.uid); // Reference to the user's document in Firestore
            const userSnap = await getDoc(userRef);
    
            if (userSnap.exists()) {
              setUser(userSnap.data()); // Set state with extra user data
            } else {
              console.log("No such document!");
            }
          }
        };
    
        fetchUserData();
    }, []);

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    const goToUserProfile = () => {
        navigate('/user-profile'); // Navigate to UserProfile
    };

    if (!user) {
        return <LoadingIndicator />;
      }

    return (
    <div style={protectedStyle}>
        <VideoRecorder/>
        <h1>Protected Page</h1>
        <p>Hi {user.name}</p>
        <p>Congratulations! You've accessed the protected content.</p>
        <button onClick={handleLogout} style={buttonStyle}>Logout</button>
        <button onClick={goToUserProfile}>View User Profile</button> {/* Button to redirect */}
    </div>
    );
}

export default ProtectedPage;
