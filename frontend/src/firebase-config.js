import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAa_wTYAYT8mdJjjokSAmT9f-Xm77JWCZw",
    authDomain: "calgaryhacks2024-1ff41.firebaseapp.com",
    projectId: "calgaryhacks2024-1ff41",
    storageBucket: "calgaryhacks2024-1ff41.appspot.com",
    messagingSenderId: "451547274582",
    appId: "1:451547274582:web:603eabb5b10b4bb0af0af7",
    measurementId: "G-H99RY4HWE3"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export default app;

