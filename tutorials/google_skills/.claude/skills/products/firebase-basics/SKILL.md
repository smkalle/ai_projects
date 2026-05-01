---
name: firebase-basics
description: Set up and use Firebase for mobile and web app development. Use when asked to initialize a Firebase project, configure Firebase Authentication (Google, email, phone sign-in), set up Firestore or Realtime Database, configure Firebase Hosting, or manage Firebase project settings.
when_to_use: Firebase project initialization, Auth configuration, Firestore security rules, Firebase Hosting setup, Cloud Functions for Firebase, Firebase Analytics
---

# Firebase Basics Skill

Use this skill when working with Firebase projects, Authentication, Firestore, or Firebase Hosting.

## Project Initialization

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize project
firebase init
# Select: Hosting, Firestore, Functions, Auth

# Deploy
firebase deploy
```

## Firebase Authentication

### Enable Providers (via console or CLI)

```bash
# List current Auth config
firebase auth:export --format=json
```

### Google Sign-In

```json
{
  "signInMethods": ["google.com"],
  "providerDetails": {
    "google.com": {
      "clientId": "YOUR_WEB_CLIENT_ID",
      "clientSecret": "YOUR_CLIENT_SECRET"
    }
  }
}
```

### Email/Password

```javascript
// Firebase Auth REST API — sign up
curl -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass","returnSecureToken":true}'
```

## Firestore

### Security Rules (rules.rules)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    match /posts/{postId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null &&
        (resource.data.authorId == request.auth.uid || request.auth.token.admin == true);
    }
  }
}
```

### Firestore REST API

```bash
# Create document
curl -X POST \
  "https://firestore.googleapis.com/v1/projects/my-project/databases/(default)/documents/posts?key=API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fields":{"title":{"stringValue":"Hello"},"authorId":{"stringValue":"uid1"}}}'
```

### Firestore Indexes

```json
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "posts",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "authorId", "order": "ASCENDING"},
        {"fieldPath": "createdAt", "order": "DESCENDING"}
      ]
    }
  ]
}
```

## Firebase Hosting

```bash
# firebase.json
{
  "hosting": {
    "public": "public",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      {"source": "/api/**", "function": "api"},
      {"source": "**", "destination": "/index.html"}
    ]
  }
}

# Deploy
firebase deploy --only hosting
```

## Firebase Config

```javascript
const firebaseConfig = {
  apiKey: "API_KEY",
  authDomain: "my-project.firebaseapp.com",
  projectId: "my-project",
  storageBucket: "my-project.appspot.com",
  messagingSenderId: "SENDER_ID",
  appId: "APP_ID"
};
```
