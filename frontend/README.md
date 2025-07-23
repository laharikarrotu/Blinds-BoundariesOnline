# Blinds & Boundaries Online - Frontend

A modern React TypeScript application for virtually trying on blinds with advanced features including user authentication, favorites, and social sharing.

## 🚀 Features

### Core Features
- **Virtual Blinds Try-On**: Upload window photos and see blinds virtually installed
- **Multiple Blind Options**: Choose from various blind textures and colors
- **Real-time Processing**: AI-powered window detection and blind overlay

### Advanced Features
- **🔐 Auth0 Authentication**: Secure user login and account management
- **❤️ Favorites System**: Save and manage your favorite blind combinations
- **📱 Social Sharing**: Share results on Facebook, Twitter, LinkedIn, and Pinterest
- **💾 Download Results**: Download high-quality images of your try-on results
- **📋 Copy Links**: Easy sharing with generated URLs

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pnpm install
```

### 2. Configure Auth0

1. **Create an Auth0 Account**:
   - Go to [Auth0.com](https://auth0.com) and create a free account
   - Create a new application (Single Page Application)

2. **Get Your Credentials**:
   - Copy your **Domain** and **Client ID** from the Auth0 dashboard

3. **Update Configuration**:
   - Open `src/auth0-config.ts`
   - Replace the placeholder values:
   ```typescript
   export const auth0Config = {
     domain: "your-domain.auth0.com", // Your Auth0 domain
     clientId: "your-client-id", // Your Auth0 client ID
     authorizationParams: {
       redirect_uri: window.location.origin,
       audience: "your-api-audience", // Optional: if you have an API
     },
   };
   ```

4. **Configure Auth0 Settings**:
   - In your Auth0 dashboard, go to your application settings
   - Add `http://localhost:5173` to **Allowed Callback URLs**
   - Add `http://localhost:5173` to **Allowed Logout URLs**
   - Add `http://localhost:5173` to **Allowed Web Origins**

### 3. Start Development Server
```bash
pnpm run dev
```

The application will be available at `http://localhost:5173`

## 📁 Project Structure

```
src/
├── components/
│   ├── ImageUpload.tsx      # File upload with progress
│   ├── BlindsSelector.tsx   # Blind texture and color selection
│   ├── TryOnButton.tsx      # Process try-on requests
│   ├── Favorites.tsx        # User favorites management
│   ├── ShareResults.tsx     # Social sharing functionality
│   ├── LoginButton.tsx      # Auth0 login button
│   └── LogoutButton.tsx     # Auth0 logout button
├── auth0-config.ts          # Auth0 configuration
├── App.tsx                  # Main application component
├── main.tsx                 # Application entry point
└── index.css               # Tailwind CSS styles
```

## 🔧 API Endpoints

The frontend expects these backend endpoints:

- `POST /upload` - Upload window images
- `GET /blinds` - Get available blind options
- `POST /try-on` - Process try-on request
- `GET /favorites` - Get user favorites (requires auth)
- `POST /favorites` - Save favorite (requires auth)
- `DELETE /favorites/{id}` - Delete favorite (requires auth)

## 🎨 Styling

Built with **Tailwind CSS** for modern, responsive design:
- Gradient backgrounds
- Card-based layouts
- Responsive grid systems
- Interactive hover effects
- Loading animations

## 🔐 Authentication Flow

1. **Login**: Users click "Log In" to authenticate with Auth0
2. **Profile**: User profile picture and name displayed in header
3. **Protected Features**: Favorites require authentication
4. **Logout**: Secure logout with redirect to home page

## 📱 Social Sharing

Share results on multiple platforms:
- **Facebook**: Direct sharing with custom text
- **Twitter**: Tweet with hashtags and image
- **LinkedIn**: Professional sharing
- **Pinterest**: Pin with image and description
- **Copy Link**: Generate shareable URLs

## 🚀 Deployment

### Build for Production
```bash
pnpm run build
```

### Environment Variables
Create a `.env` file for production:
```env
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_API_URL=https://your-backend-url.com
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support or questions:
- Email: support@blindsboundaries.com
- GitHub Issues: Create an issue in this repository 