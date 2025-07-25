import { useState, useEffect } from 'react';
import { API_ENDPOINTS, API_BASE_URL } from '../config';



interface BlindsSelectorProps {
  onChange: (blindName: string, color: string) => void;
}

export default function BlindsSelector({ onChange }: BlindsSelectorProps) {
  const [blinds, setBlinds] = useState<string[]>([]);
  const [selectedBlind, setSelectedBlind] = useState<string>('');
  const [selectedColor, setSelectedColor] = useState<string>('#ffffff');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

  const colors = [
    { name: 'White', value: '#ffffff' },
    { name: 'Beige', value: '#f5f5dc' },
    { name: 'Gray', value: '#808080' },
    { name: 'Brown', value: '#8b4513' },
    { name: 'Black', value: '#000000' },
    { name: 'Blue', value: '#0000ff' },
    { name: 'Green', value: '#008000' },
    { name: 'Red', value: '#ff0000' },
  ];

  useEffect(() => {
    fetchBlinds();
  }, []);

  useEffect(() => {
    if (selectedBlind && selectedColor) {
      onChange(selectedBlind, selectedColor);
    }
  }, [selectedBlind, selectedColor, onChange]);

  const fetchBlinds = async () => {
    try {
      console.log('Fetching blinds from:', API_ENDPOINTS.BLINDS_LIST);
      const response = await fetch(API_ENDPOINTS.BLINDS_LIST);
      if (!response.ok) {
        throw new Error(`Failed to fetch blinds: ${response.status}`);
      }
      const data = await response.json();
      console.log('Blinds data received:', data);
      setBlinds(data.blinds || []);
    } catch (err) {
      console.error('Error fetching blinds:', err);
      setError('Failed to load blinds. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageError = (blindName: string) => {
    console.warn(`Failed to load image for blind: ${blindName}`);
    setImageErrors(prev => new Set(prev).add(blindName));
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-2 text-gray-600">Loading blinds...</p>
      </div>
    );
  }

  if (error) {
    return <div className="p-4 bg-red-100 text-red-800 rounded text-center">{error}</div>;
  }

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-2xl mx-auto mt-8 bg-white shadow">
      <h2 className="text-xl font-semibold mb-4 text-center">Select Blind Texture & Color</h2>
      
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
        {blinds.map((blind) => (
          <div
            key={blind}
            className={`cursor-pointer rounded-lg border-2 transition-all ${
              selectedBlind === blind
                ? 'border-blue-500 shadow-lg'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedBlind(blind)}
          >
            {!imageErrors.has(blind) ? (
              <img
                src={`${API_BASE_URL}/blinds/${blind}`}
                alt={blind}
                className="w-full h-20 object-cover bg-gray-100"
                onError={() => handleImageError(blind)}
                onLoad={() => console.log(`Successfully loaded image for: ${blind}`)}
              />
            ) : (
              <div className="w-full h-20 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500 text-xs">Image not available</span>
              </div>
            )}
            <p className="text-sm text-center p-2 font-medium">{blind}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-center gap-4">
        <label htmlFor="blind-color" className="font-medium text-gray-700">Blind Color:</label>
        <div className="flex gap-2">
          {colors.map((color) => (
            <div key={color.value} className="flex items-center">
              <input
                type="radio"
                id={`color-${color.value}`}
                name="blind-color"
                value={color.value}
                checked={selectedColor === color.value}
                onChange={(e) => setSelectedColor(e.target.value)}
                className="sr-only"
              />
              <label
                htmlFor={`color-${color.value}`}
                className="w-10 h-10 border-2 border-gray-300 rounded cursor-pointer"
                style={{ backgroundColor: color.value }}
              >
                {selectedColor === color.value && (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-4 h-4 bg-white rounded-full"></div>
                  </div>
                )}
              </label>
              <span className="ml-2 text-gray-600">{color.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 