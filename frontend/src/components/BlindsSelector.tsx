import { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';

interface BlindsSelectorProps {
  onBlindSelect: (blindData: BlindData) => void;
}

interface BlindData {
  mode: 'texture' | 'generated';
  blindName?: string;
  blindType?: string;
  color: string;
  material?: string;
}

interface BlindsData {
  texture_blinds: string[];
  generated_patterns: string[];
  materials: string[];
  texture_count: number;
  pattern_count: number;
}

export default function BlindsSelector({ onBlindSelect }: BlindsSelectorProps) {
  const [blindsData, setBlindsData] = useState<BlindsData | null>(null);
  const [selectedMode, setSelectedMode] = useState<'texture' | 'generated'>('texture');
  const [selectedBlind, setSelectedBlind] = useState<string>('');
  const [selectedBlindType, setSelectedBlindType] = useState<string>('');
  const [selectedColor, setSelectedColor] = useState<string>('#808080');
  const [selectedMaterial, setSelectedMaterial] = useState<string>('fabric');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBlinds();
  }, []);

  const fetchBlinds = async () => {
    try {
      console.log('Fetching blinds from:', API_ENDPOINTS.BLINDS_LIST);
      const response = await fetch(API_ENDPOINTS.BLINDS_LIST);
      
      if (!response.ok) {
        throw new Error('Failed to fetch blinds');
      }
      
      const data = await response.json();
      console.log('Blinds data received:', data);
      setBlindsData(data);
      
      // Set default selections
      if (data.texture_blinds.length > 0) {
        setSelectedBlind(data.texture_blinds[0]);
      }
      if (data.generated_patterns.length > 0) {
        setSelectedBlindType(data.generated_patterns[0]);
      }
      
    } catch (err) {
      console.error('Error fetching blinds:', err);
      setError('Failed to load blinds');
    } finally {
      setLoading(false);
    }
  };

  const handleBlindSelect = () => {
    const blindData: BlindData = {
      mode: selectedMode,
      color: selectedColor,
    };

    if (selectedMode === 'texture') {
      blindData.blindName = selectedBlind;
    } else {
      blindData.blindType = selectedBlindType;
      blindData.material = selectedMaterial;
    }

    onBlindSelect(blindData);
  };

  const handleImageLoad = (imageName: string) => {
    console.log('Successfully loaded image for:', imageName);
  };

  const handleImageError = (imageName: string) => {
    console.error('Failed to load image for:', imageName);
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-600"></div>
        <p className="mt-2 text-gray-600">Loading blinds...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error: {error}</p>
        <button 
          onClick={fetchBlinds}
          className="mt-2 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <div className="flex space-x-4">
        <button
          onClick={() => setSelectedMode('texture')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedMode === 'texture'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Pre-made Textures ({blindsData?.texture_count || 0})
        </button>
        <button
          onClick={() => setSelectedMode('generated')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedMode === 'generated'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Custom Patterns ({blindsData?.pattern_count || 0})
        </button>
      </div>

      {/* Texture Mode */}
      {selectedMode === 'texture' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Select Pre-made Texture</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {blindsData?.texture_blinds.map((blind) => (
              <div
                key={blind}
                onClick={() => setSelectedBlind(blind)}
                className={`cursor-pointer rounded-lg border-2 transition-all hover:shadow-lg ${
                  selectedBlind === blind
                    ? 'border-indigo-600 shadow-lg'
                    : 'border-gray-300 hover:border-indigo-400'
                }`}
              >
                <img
                  src={`${API_ENDPOINTS.BLINDS_LIST.replace('/blinds-list', '/blinds')}/${blind}`}
                  alt={blind}
                  className="w-full h-24 object-cover rounded-t-lg"
                  onLoad={() => handleImageLoad(blind)}
                  onError={() => handleImageError(blind)}
                />
                <div className="p-2 text-center">
                  <p className="text-sm text-gray-700 truncate">{blind}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Mode */}
      {selectedMode === 'generated' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Customize Your Blinds</h3>
          
          {/* Blind Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Blind Type
            </label>
            <select
              value={selectedBlindType}
              onChange={(e) => setSelectedBlindType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {blindsData?.generated_patterns.map((pattern) => (
                <option key={pattern} value={pattern}>
                  {pattern.charAt(0).toUpperCase() + pattern.slice(1)} Blinds
                </option>
              ))}
            </select>
          </div>

          {/* Material Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Material
            </label>
            <select
              value={selectedMaterial}
              onChange={(e) => setSelectedMaterial(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {blindsData?.materials.map((material) => (
                <option key={material} value={material}>
                  {material.charAt(0).toUpperCase() + material.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Color Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Color
        </label>
        <div className="flex items-center space-x-4">
          <input
            type="color"
            value={selectedColor}
            onChange={(e) => setSelectedColor(e.target.value)}
            className="w-12 h-12 border border-gray-300 rounded cursor-pointer"
          />
          <input
            type="text"
            value={selectedColor}
            onChange={(e) => setSelectedColor(e.target.value)}
            placeholder="#808080"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Preview */}
      <div className="bg-gray-100 p-4 rounded-lg">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Preview</h4>
        <div className="text-sm text-gray-600">
          <p><strong>Mode:</strong> {selectedMode}</p>
          {selectedMode === 'texture' && (
            <p><strong>Texture:</strong> {selectedBlind}</p>
          )}
          {selectedMode === 'generated' && (
            <>
              <p><strong>Type:</strong> {selectedBlindType}</p>
              <p><strong>Material:</strong> {selectedMaterial}</p>
            </>
          )}
          <p><strong>Color:</strong> {selectedColor}</p>
        </div>
      </div>

      {/* Select Button */}
      <button
        onClick={handleBlindSelect}
        disabled={!selectedBlind && !selectedBlindType}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
          (!selectedBlind && !selectedBlindType)
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-indigo-600 text-white hover:bg-indigo-700'
        }`}
      >
        Select Blinds
      </button>
    </div>
  );
} 