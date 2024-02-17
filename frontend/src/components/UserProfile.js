import React, { useEffect, useState } from 'react';
import { auth } from '../firebase-config';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { db } from '../firebase-config';
import { doc, getDoc } from "firebase/firestore"; 

const userProfileStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  minHeight: '100vh',
  backgroundColor: '#6A5ACD', // Indigo background, same as the ProtectedPage
  color: '#FFFFFF', // White text for contrast
  gap: '20px',
};

const userInfoStyle = {
  backgroundColor: '#FFFFFF', // White background for the user info cards
  color: '#6A5ACD', // Indigo text to match the page background
  padding: '20px',
  borderRadius: '10px',
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
  margin: '10px',
  width: '80%', // Adjust as needed
  maxWidth: '500px', // Adjust as needed
  textAlign: 'center',
};

const backButtonStyle = {
    padding: '10px 20px',
    backgroundColor: '#FFFFFF', // White background for contrast
    color: '#6A5ACD', // Indigo text to match the page
    border: '1px solid #6A5ACD', // Indigo border
    borderRadius: '5px',
    cursor: 'pointer',
    textDecoration: 'none',
  };

function UserProfile() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate(); // Initialize useNavigate

  useEffect(() => {
    const fetchUserData = async () => {
      const user = auth.currentUser;
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

  if (!user) {
    return <div style={userProfileStyle}>No user is currently signed in.</div>;
  }

  return (
    <div style={userProfileStyle}>
      <h1>User Profile</h1>
      <div style={userInfoStyle}>
        <p><strong>Name:</strong> {user.name}</p>
        <p><strong>Email:</strong> {user.email}</p>
        {/* Render other user properties here */}
      </div>
      <button style={backButtonStyle} onClick={() => navigate(-1)}>Go Back</button> {/* Go Back button */}
    </div>
  );
}

export default UserProfile;
