// Handles basic auth of login, signup, signout using Firebase Auth
import { auth, db } from './firebase-config';
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "firebase/auth";
import { doc, setDoc } from 'firebase/firestore'; 
export const login = (email, password) => {
    return signInWithEmailAndPassword(auth, email, password);
};

export const signup = async (name, email, password) => {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
    
        // Reference to a document in the "users" collection with the new user's UID
        const userRef = doc(db, "users", user.uid);
    
        // Set document with additional user data
        await setDoc(userRef, {
          // Default data structure; you can add more fields as needed
          name: name,
          email: email,
          createdAt: new Date(),
           // Spread any additional data you want to store for the user
        });
    
        console.log("User signed up and document created in Firestore.");
      } catch (error) {
        console.error("Error signing up:", error.message);
      }
};

export const logout = () => {
    return signOut(auth);
};
