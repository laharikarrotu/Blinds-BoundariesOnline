import { useState } from 'react';
import { API_ENDPOINTS } from '../config';

interface TryOnButtonProps {
  imageId: string;
  blindName: string;
  color: string;
  onComplete?: (url: string) => void;
}

export default function TryOnButton({ imageId, blindName, color, onComplete }: TryOnButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTryOn = async () => {
    if (!imageId || !blindName) {
      setError('Please upload an image and select a blind first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResultUrl(null);

    try {
      // Step 1: Detect window first
      console.log('Detecting window...');
      const detectParams = new URLSearchParams({ image_id: imageId });
      const detectResponse = await fetch(`${API_ENDPOINTS.DETECT_WINDOW}?${detectParams}`, {
        method: 'POST',
      });

      if (!detectResponse.ok) {
        throw new Error('Window detection failed');
      }

      console.log('Window detection successful, trying on blinds...');
      
      // Step 2: Try on blinds
      const params = new URLSearchParams({
        image_id: imageId,
        blind_name: blindName,
      });
      if (color) {
        params.append('color', color);
      }
      
      const response = await fetch(`${API_ENDPOINTS.TRY_ON}?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Try-on failed');
      }

      const result = await response.json();
      setResultUrl(result.result_url);
      onComplete?.(result.result_url);
      
    } catch (err) {
      setError('Failed to process try-on. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const isDisabled = !imageId || !blindName || isProcessing;

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
          />
          <div className="mt-4">
            <a
              href={resultUrl}
              download="blinds-tryon-result.png"
              className="inline-block bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Download Result
            </a>
          </div>
        </div>
      )}
    </div>
  );
} 