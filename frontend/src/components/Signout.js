import React from 'react';
import { logout } from '../authService';

const Signout = () => {
    const handleSignout = async () => {
        try {
            await logout();
            console.log('Signed out successfully!');
        } catch (error) {
            console.error('Failed to sign out', error);
        }
    };

    return (
        <button onClick={handleSignout}>Sign Out</button>
    );
}

export default Signout;
