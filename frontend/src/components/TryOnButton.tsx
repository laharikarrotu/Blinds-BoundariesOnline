import { useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { API_ENDPOINTS } from '../config';
import { databaseService } from '../services/database';

interface BlindData {
  mode: 'texture' | 'generated';
  blindName?: string;
  blindType?: string;
  color: string;
  material?: string;
}

interface TryOnButtonProps {
  imageId: string | null;
  blindData: BlindData | null;
  onComplete?: (url: string) => void;
}

export default function TryOnButton({ imageId, blindData, onComplete }: TryOnButtonProps) {
  const { isAuthenticated, user } = useAuth0();
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTryOn = async () => {
    if (!imageId || !blindData) {
      setError('Please upload an image and select a blind first');
      return;
    }

    // Validate blind data based on mode
    if (blindData.mode === 'texture' && !blindData.blindName) {
      setError('Please select a blind texture');
      return;
    }
    if (blindData.mode === 'generated' && !blindData.blindType) {
      setError('Please select a blind type');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResultUrl(null);

    try {
      // Step 1: Detect window first
      console.log('Detecting window...');
      const detectParams = new URLSearchParams({ image_id: imageId });
      
      // Add timeout to the fetch request
      const detectController = new AbortController();
      const detectTimeout = setTimeout(() => detectController.abort(), 60000); // 60 second timeout
      
      const detectResponse = await fetch(`${API_ENDPOINTS.DETECT_WINDOW}?${detectParams}`, {
        method: 'POST',
        signal: detectController.signal,
      });

      clearTimeout(detectTimeout);

      if (!detectResponse.ok) {
        const errorText = await detectResponse.text();
        console.error('Window detection failed:', errorText);
        throw new Error(`Window detection failed: ${detectResponse.status} ${detectResponse.statusText}`);
      }

      console.log('Window detection successful, trying on blinds...');
      
      // Step 2: Try on blinds
      const params = new URLSearchParams({
        image_id: imageId,
        mode: blindData.mode,
        color: blindData.color,
      });

      // Add mode-specific parameters
      if (blindData.mode === 'texture') {
        params.append('blind_name', blindData.blindName!);
      } else {
        params.append('blind_type', blindData.blindType!);
        params.append('material', blindData.material || 'fabric');
      }
      
      // Add timeout to the try-on request
      const tryOnController = new AbortController();
      const tryOnTimeout = setTimeout(() => tryOnController.abort(), 120000); // 2 minute timeout for try-on
      
      console.log('Fetch request:', `${API_ENDPOINTS.TRY_ON}?${params}`);
      
      const response = await fetch(`${API_ENDPOINTS.TRY_ON}?${params}`, {
        method: 'POST',
        signal: tryOnController.signal,
      });

      clearTimeout(tryOnTimeout);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Try-on failed:', errorText);
        throw new Error(`Try-on failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Try-on result:', result);
      
      if (result.result_url) {
        setResultUrl(result.result_url);
        onComplete?.(result.result_url);

        // Save to history if user is authenticated
        if (isAuthenticated && user?.sub) {
          try {
            await databaseService.addToHistory({
              userId: user.sub,
              imageId,
              blindName: blindData.mode === 'texture' ? blindData.blindName! : blindData.blindType!,
              blindType: blindData.blindType,
              color: blindData.color,
              material: blindData.material,
              resultUrl: result.result_url
            });
            console.log('Saved to history successfully');
          } catch (historyError) {
            console.error('Failed to save to history:', historyError);
            // Don't show error to user as this is not critical
          }
        }
      } else {
        console.warn('No result_url in response:', result);
        setError('Try-on completed but no result URL was returned');
      }
      
    } catch (err) {
      console.error('Try-on error:', err);
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          setError('Request timed out. Please try again.');
        } else {
          setError(`Failed to process try-on: ${err.message}`);
        }
      } else {
        setError('Failed to process try-on. Please try again.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const isDisabled = !imageId || !blindData || isProcessing;

  return (
    <div className="mt-8 text-center">
      <button
        onClick={handleTryOn}
        disabled={isDisabled}
        className={`px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-200 ${
          isDisabled
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
        }`}
      >
        {isProcessing ? (
          <>
            <span className="inline-block animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white align-middle mr-2"></span>
            Processing...
          </>
        ) : (
          'Try On Blinds'
        )}
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-800 rounded text-center">
          ❌ {error}
        </div>
      )}

      {resultUrl && (
        <div className="mt-6">
          <div className="text-gray-700 font-medium mb-2">Result:</div>
          <img 
            src={resultUrl} 
            alt="Try-on result" 
            className="max-w-full rounded-lg mx-auto border shadow"
            onError={(e) => {
              console.error('Failed to load result image:', e);
              setError('Failed to load result image. Please try again.');
            }}
          />
          <div className="mt-4 space-x-4">
            <a
              href={resultUrl}
              download="blinds-tryon-result.png"
              className="inline-block bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Download Result
            </a>
            {isAuthenticated && (
              <button
                onClick={async () => {
                  if (!user?.sub) return;
                  try {
                    await databaseService.addFavorite({
                      userId: user.sub,
                      imageId: imageId!,
                      blindName: blindData!.mode === 'texture' ? blindData!.blindName! : blindData!.blindType!,
                      blindType: blindData!.blindType,
                      color: blindData!.color,
                      material: blindData!.material,
                      resultUrl
                    });
                    alert('Added to favorites!');
                  } catch (err) {
                    console.error('Failed to add to favorites:', err);
                    alert('Failed to add to favorites');
                  }
                }}
                className="inline-block bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                ❤️ Add to Favorites
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 