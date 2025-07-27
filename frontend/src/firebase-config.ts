import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

// Your Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyCyJUpFCXdoZPwf7YZmAv5LXBmScD2KpGA",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "blinds-boundaries.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "blinds-boundaries",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "blinds-boundaries.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "1098758278430",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:1098758278430:web:93f375eb66263080d78d0f",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-XYHJME3DVJ"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore Database
export const db = getFirestore(app);

// Initialize Firebase Auth (for future use)
export const auth = getAuth(app);

// Initialize Firebase Analytics
export const analytics = getAnalytics(app);

export default app; 