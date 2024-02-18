import React, { useEffect, useState } from 'react';
import { auth } from '../firebase-config';
import LoadingIndicator from './LoadingIndicator';
import { db } from '../firebase-config';
import { doc, getDoc } from "firebase/firestore"; 
import { useLocation } from 'react-router-dom';

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

const ReportPage = () => {
    const [user, setUser] = useState(null);
    const [data, setData] = useState(null);
    let location = useLocation(); 
    let queryParams = new URLSearchParams(location.search);
    let context_chosen = queryParams.get('context');

    useEffect(() => {
        const handleReport = async () => {
          try {
            console.log('Fetching report...');
            const response = await fetch('http://127.0.0.1:5000/reportGenerator/generateReport', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ reportType: context_chosen}),
            });

            if (!response.ok) {
              throw new Error('Network response was not ok');
            }

            const result = await response.json();
            setData(result);
          } catch (error) {
            console.error('There was an error!', error);
          }
        };

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

        handleReport();
        fetchUserData();
    }, []);


    if (!user) {
        return <LoadingIndicator />;
      }

    return (
    <div style={protectedStyle}>
        <h1>Protected Page</h1>
        <p>Hi {user.name}</p>
        <p>Here is your interaction stats!</p>
        <div>
        {data ? (
          <div>
            <h2>Processed Data:</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
          ) : (
            <p>Loading...</p>
        )}
    </div>
    </div>
    );
}

export default ReportPage;
