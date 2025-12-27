import { useState, useEffect } from 'react';
import { SpeedInsights } from "@vercel/speed-insights/react"
// import { useAuth0 } from '@auth0/auth0-react'; // Disabled until Auth0 is configured
import ImageUpload from './components/ImageUpload';
import BlindsSelector from './components/BlindsSelector';
import TryOnButton from './components/TryOnButton';
import Favorites from './components/Favorites';
import History from './components/History';
import ShareResults from './components/ShareResults';
import LoginButton from './components/LoginButton';
import LogoutButton from './components/LogoutButton';
import RealTimePreview from './components/RealTimePreview';
import AdvancedColorPicker from './components/AdvancedColorPicker';
import RoomTypeSelector from './components/RoomTypeSelector';
import LightingEffects from './components/LightingEffects';
import { API_BASE_URL } from './config';

interface BlindData {
  mode: 'texture' | 'generated';
  blindName?: string;
  blindType?: string;
  color: string;
  material?: string;
}

function App() {
  // Temporarily disable Auth0 until properly configured
  // const { isAuthenticated, isLoading } = useAuth0();
  const isAuthenticated = true; // Allow access without login for now
  const isLoading = false; // Not loading since Auth0 is disabled
  const [imageId, setImageId] = useState<string | null>(null);
  const [blindData, setBlindData] = useState<BlindData | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'try-on' | 'favorites' | 'history'>('try-on');
  const [selectedRoom, setSelectedRoom] = useState('');
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [showAdvancedFeatures, setShowAdvancedFeatures] = useState(false);
  const [selectedLighting, setSelectedLighting] = useState('day');
  const [hasError, setHasError] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Add debugging to track any routing issues
  useEffect(() => {
    console.log('App mounted, current URL:', window.location.href);
    console.log('Current pathname:', window.location.pathname);
    
    // Check if there are any unexpected requests being made
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      console.log('Fetch request:', args[0]);
      return originalFetch.apply(this, args);
    };

    // Health check for API
    const checkApiHealth = async () => {
      try {
        console.log('Checking API health...');
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
          const data = await response.json();
          console.log('API health check successful:', data);
        } else {
          console.error('API health check failed:', response.status);
        }
      } catch (error) {
        console.error('API health check error:', error);
      }
    };

    checkApiHealth();

    // Monitor for any navigation or routing issues
    const handleBeforeUnload = () => {
      console.log('Page is about to unload');
    };

    const handleError = (event: ErrorEvent) => {
      console.error('Global error:', event.error);
      setHasError(true);
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      setHasError(true);
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      // Restore original fetch
      window.fetch = originalFetch;
    };
  }, [API_BASE_URL]);



  // Error boundary component
  if (hasError) {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center">
        <div className="text-center p-8">
          <h1 className="text-2xl font-bold text-red-800 mb-4">Something went wrong</h1>
          <p className="text-red-600 mb-4">We encountered an error while loading the application.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  const handleTryOnComplete = (url: string) => {
    setResultUrl(url);
  };

  const handleImageUpload = (id: string, imageUrl?: string) => {
    setImageId(id);
    if (imageUrl) {
      setOriginalImageUrl(imageUrl);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 flex flex-col font-sans">
      <SpeedInsights />
      {/* Header */}
      <header className="bg-indigo-700 text-white py-5 shadow-lg">
        <div className="container mx-auto flex items-center justify-between px-4">
          <span className="font-extrabold text-2xl tracking-tight">Blinds & Boundaries Online</span>
          <nav className="flex items-center gap-6">
            <button
              onClick={() => setCurrentStep('try-on')}
              className={`text-white hover:underline font-medium ${
                currentStep === 'try-on' ? 'underline' : ''
              }`}
            >
              Try On
            </button>
            <button
              onClick={() => setCurrentStep('favorites')}
              className={`text-white hover:underline font-medium ${
                currentStep === 'favorites' ? 'underline' : ''
              }`}
            >
              Favorites
            </button>
            <button
              onClick={() => setCurrentStep('history')}
              className={`text-white hover:underline font-medium ${
                currentStep === 'history' ? 'underline' : ''
              }`}
            >
              History
            </button>
            <button
              onClick={() => setShowAdvancedFeatures(!showAdvancedFeatures)}
              className={`text-white hover:underline font-medium ${
                showAdvancedFeatures ? 'underline' : ''
              }`}
            >
              {showAdvancedFeatures ? 'Hide' : 'Show'} Advanced
            </button>
            {isAuthenticated ? <LogoutButton /> : <LoginButton />}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-10">
        {currentStep === 'try-on' ? (
          <>
            <div className="text-center mb-10">
              <h1 className="text-4xl font-extrabold mb-3 text-indigo-800 drop-shadow">
                Virtually Try On Blinds for Your Space
              </h1>
              <p className="text-lg text-gray-600">
                Upload a photo, select a blind, and see how it looks instantly!
              </p>
            </div>

            <div className="flex flex-col gap-10 max-w-4xl mx-auto">
              {/* Step 1: Upload Image */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Step 1: Upload Your Window Photo</h2>
                <ImageUpload onUpload={(id) => handleImageUpload(id, '')} />
              </div>

              {/* Advanced Features */}
              {showAdvancedFeatures && (
                <>
                  {/* Room Type Selection */}
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Room Type Selection</h2>
                    <RoomTypeSelector selectedRoom={selectedRoom} onRoomChange={setSelectedRoom} />
                  </div>

                  {/* Advanced Color Picker */}
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Advanced Color Selection</h2>
                    <AdvancedColorPicker 
                      selectedColor={blindData?.color || '#ffffff'} 
                      onColorChange={(color) => setBlindData(prev => prev ? {...prev, color} : null)} 
                    />
                  </div>

                  {/* Lighting Effects */}
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Lighting Effects</h2>
                    <LightingEffects onLightingChange={setSelectedLighting} />
                    <p className="text-center text-sm text-gray-600 mt-2">
                      Current lighting: {selectedLighting}
                    </p>
                  </div>
                </>
              )}

              {/* Step 2: Select Blinds */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Step 2: Choose Your Blinds</h2>
                <BlindsSelector onBlindSelect={setBlindData} />
              </div>

              {/* Real-time Preview */}
              {imageId && blindData && originalImageUrl && (
                <RealTimePreview 
                  imageId={imageId}
                  selectedBlind={blindData.mode === 'texture' ? blindData.blindName! : blindData.blindType!}
                  selectedColor={blindData.color}
                  originalImageUrl={originalImageUrl}
                />
              )}

              {/* Step 3: Try On */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Step 3: Try On Your Blinds</h2>
                <TryOnButton 
                  imageId={imageId} 
                  blindData={blindData}
                  onComplete={handleTryOnComplete}
                />
              </div>

              {/* Step 4: Share Results */}
              {resultUrl && blindData && (
                <div className="bg-white rounded-xl shadow-lg p-8">
                  <ShareResults 
                    resultUrl={resultUrl}
                    blindName={blindData.mode === 'texture' ? blindData.blindName! : blindData.blindType!}
                    color={blindData.color}
                  />
                </div>
              )}

              {/* Instructions */}
              <div className="mt-16 max-w-2xl mx-auto">
                <div className="bg-blue-50 rounded-lg p-6">
                  <h3 className="text-xl font-semibold mb-4 text-blue-800">How it works:</h3>
                  <ol className="space-y-2 text-blue-700">
                    <li className="flex items-start">
                      <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">1</span>
                      Upload a clear photo of your window or room
                    </li>
                    <li className="flex items-start">
                      <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">2</span>
                      Choose from our selection of blind textures and colors
                    </li>
                    <li className="flex items-start">
                      <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">3</span>
                      Click "Try On" to see your blinds virtually installed
                    </li>
                    <li className="flex items-start">
                      <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold mr-3 mt-0.5">4</span>
                      Share your results and save to favorites (login required)
                    </li>
                  </ol>
                </div>
              </div>
            </div>
          </>
        ) : currentStep === 'favorites' ? (
          <Favorites />
        ) : (
          <History />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-indigo-800 text-white py-4 text-center mt-8 shadow-inner">
        &copy; {new Date().getFullYear()} Blinds & Boundaries Online. All rights reserved.
      </footer>
    </div>
  );
}

export default App; 