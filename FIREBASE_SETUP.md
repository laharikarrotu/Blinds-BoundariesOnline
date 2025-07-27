# 🔥 Firebase Setup Guide

## **Step 1: Create Firebase Project**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"**
3. Enter project name: `blinds-boundaries-online`
4. Enable Google Analytics (optional)
5. Click **"Create project"**

## **Step 2: Enable Firestore Database**

1. In Firebase Console, go to **"Firestore Database"**
2. Click **"Create database"**
3. Choose **"Start in test mode"** (for development)
4. Select a location (choose closest to your users)
5. Click **"Done"**

## **Step 3: Get Firebase Config**

1. In Firebase Console, go to **"Project settings"** (gear icon)
2. Scroll down to **"Your apps"**
3. Click **"Add app"** → **"Web"**
4. Register app with name: `blinds-boundaries-frontend`
5. Copy the config object

## **Step 4: Add Environment Variables**

Create a `.env` file in the `frontend/` directory:

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key-here
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your-app-id-here
```

## **Step 5: Security Rules (Optional)**

In Firestore Database → Rules, you can set up security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow users to read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Allow users to manage their own favorites
    match /favorites/{favoriteId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    // Allow users to manage their own history
    match /history/{historyId} {
      allow read, write: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
    
    // Allow users to manage their own preferences
    match /userPreferences/{userId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
  }
}
```

## **Step 6: Test the Integration**

1. Start your frontend: `cd frontend && pnpm dev`
2. Login with Auth0
3. Try uploading an image and using the try-on feature
4. Check that favorites and history are saved

## **Database Collections**

The app will automatically create these collections:

- **`users`** - User profiles and preferences
- **`favorites`** - Saved blind combinations
- **`history`** - Try-on history
- **`userPreferences`** - User settings and defaults

## **Troubleshooting**

### **Firebase Not Connected**
- Check that environment variables are correct
- Verify Firebase project is created
- Check browser console for errors

### **Permission Denied**
- Make sure Firestore is in test mode
- Check security rules if using production mode

### **Data Not Saving**
- Verify user is authenticated
- Check browser console for Firebase errors
- Ensure Firestore is enabled in Firebase Console

## **Next Steps**

Once Firebase is working:
1. Test all features (upload, try-on, favorites, history)
2. Deploy to production
3. Consider upgrading to production security rules
4. Monitor usage in Firebase Console

## **Cost Monitoring**

Firebase free tier includes:
- 1GB storage
- 50,000 reads/day
- 20,000 writes/day

Monitor usage in Firebase Console → Usage and billing. 