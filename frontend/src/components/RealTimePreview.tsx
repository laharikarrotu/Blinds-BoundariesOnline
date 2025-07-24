import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';

interface RealTimePreviewProps {
  imageId: string;
  selectedBlind: string;
  selectedColor: string;
  originalImageUrl: string;
}

export default function RealTimePreview({ 
  imageId, 
  selectedBlind, 
  selectedColor, 
  originalImageUrl 
}: RealTimePreviewProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (imageId && selectedBlind) {
      generatePreview();
    }
  }, [imageId, selectedBlind, selectedColor]);

  const generatePreview = async () => {
    if (!imageId || !selectedBlind) return;

    setIsLoading(true);
    setError(null);

    try {
      // Step 1: Detect window
      const detectParams = new URLSearchParams({ image_id: imageId });
      const detectResponse = await fetch(`${API_ENDPOINTS.DETECT_WINDOW}?${detectParams}`, {
        method: 'POST',
      });

      if (!detectResponse.ok) {
        throw new Error('Window detection failed');
      }

      // Step 2: Generate preview
      const params = new URLSearchParams({
        image_id: imageId,
        blind_name: selectedBlind,
      });
      if (selectedColor) {
        params.append('color', selectedColor);
      }
      
      const response = await fetch(`${API_ENDPOINTS.TRY_ON}?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Preview generation failed');
      }

      const result = await response.json();
      setPreviewUrl(result.result_url || result.url);
      
    } catch (err) {
      setError('Failed to generate preview');
    } finally {
      setIsLoading(false);
    }
  };

  if (!imageId || !selectedBlind) {
    return (
      <div className="p-6 border border-gray-300 rounded-lg max-w-2xl mx-auto mt-8 bg-white shadow">
        <h3 className="text-lg font-semibold mb-4 text-center">Live Preview</h3>
        <div className="text-center text-gray-500">
          Upload an image and select blinds to see live preview
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-4xl mx-auto mt-8 bg-white shadow">
      <h3 className="text-lg font-semibold mb-4 text-center">Live Preview</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Original Image */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Original</h4>
          <img 
            src={originalImageUrl} 
            alt="Original" 
            className="w-full rounded-lg border shadow-sm"
          />
        </div>

        {/* Preview Image */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">With Blinds</h4>
          {isLoading ? (
            <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mb-2"></div>
                <p className="text-gray-600">Generating preview...</p>
              </div>
            </div>
          ) : previewUrl ? (
            <img 
              src={previewUrl} 
              alt="Preview with blinds" 
              className="w-full rounded-lg border shadow-sm"
            />
          ) : error ? (
            <div className="w-full h-64 bg-red-50 rounded-lg flex items-center justify-center">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            <div className="w-full h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Select blinds to see preview</p>
            </div>
          )}
        </div>
      </div>

      {previewUrl && (
        <div className="mt-4 text-center">
          <button
            onClick={() => window.open(previewUrl, '_blank')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            View Full Size
          </button>
        </div>
      )}
    </div>
  );
} 