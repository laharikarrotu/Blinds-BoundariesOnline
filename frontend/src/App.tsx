import { useState } from 'react';
// import { useAuth0 } from '@auth0/auth0-react';
import ImageUpload from './components/ImageUpload';
import BlindsSelector from './components/BlindsSelector';
import TryOnButton from './components/TryOnButton';
import Favorites from './components/Favorites';
import ShareResults from './components/ShareResults';
import LoginButton from './components/LoginButton';
import LogoutButton from './components/LogoutButton';
import RealTimePreview from './components/RealTimePreview';
import AdvancedColorPicker from './components/AdvancedColorPicker';
import RoomTypeSelector from './components/RoomTypeSelector';
import LightingEffects from './components/LightingEffects';

function App() {
  // const { isAuthenticated } = useAuth0();
  const isAuthenticated = true; // Temporarily set to true for testing
  const [imageId, setImageId] = useState('');
  const [blindName, setBlindName] = useState('');
  const [color, setColor] = useState('#ffffff');
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'try-on' | 'favorites'>('try-on');
  const [selectedRoom, setSelectedRoom] = useState('');
  const [originalImageUrl, setOriginalImageUrl] = useState<string | null>(null);
  const [showAdvancedFeatures, setShowAdvancedFeatures] = useState(false);
  const [selectedLighting, setSelectedLighting] = useState('day');

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
                    <AdvancedColorPicker selectedColor={color} onColorChange={setColor} />
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
                <BlindsSelector onChange={(b, c) => { setBlindName(b); setColor(c); }} />
              </div>

              {/* Real-time Preview */}
              {imageId && blindName && originalImageUrl && (
                <RealTimePreview 
                  imageId={imageId}
                  selectedBlind={blindName}
                  selectedColor={color}
                  originalImageUrl={originalImageUrl}
                />
              )}

              {/* Step 3: Try On */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Step 3: Try On Your Blinds</h2>
                <TryOnButton 
                  imageId={imageId} 
                  blindName={blindName} 
                  color={color}
                  onComplete={handleTryOnComplete}
                />
              </div>

              {/* Step 4: Share Results */}
              {resultUrl && (
                <div className="bg-white rounded-xl shadow-lg p-8">
                  <ShareResults 
                    resultUrl={resultUrl}
                    blindName={blindName}
                    color={color}
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
        ) : (
          <Favorites />
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