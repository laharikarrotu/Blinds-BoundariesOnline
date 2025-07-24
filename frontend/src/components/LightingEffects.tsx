import { useState } from 'react';

interface LightingEffectsProps {
  onLightingChange: (lighting: string) => void;
}

export default function LightingEffects({ onLightingChange }: LightingEffectsProps) {
  const [selectedLighting, setSelectedLighting] = useState('day');

  const lightingOptions = [
    {
      id: 'day',
      name: 'Daylight',
      description: 'Bright natural lighting',
      icon: '☀️',
      effect: 'Natural bright lighting'
    },
    {
      id: 'evening',
      name: 'Evening',
      description: 'Warm sunset lighting',
      icon: '🌅',
      effect: 'Warm golden hour lighting'
    },
    {
      id: 'night',
      name: 'Night',
      description: 'Dark ambient lighting',
      icon: '🌙',
      effect: 'Dark ambient lighting'
    },
    {
      id: 'artificial',
      name: 'Artificial',
      description: 'Indoor lighting',
      icon: '💡',
      effect: 'Warm indoor lighting'
    },
    {
      id: 'overcast',
      name: 'Overcast',
      description: 'Soft diffused lighting',
      icon: '☁️',
      effect: 'Soft diffused lighting'
    }
  ];

  const handleLightingChange = (lighting: string) => {
    setSelectedLighting(lighting);
    onLightingChange(lighting);
  };

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-2xl mx-auto mt-8 bg-white shadow">
      <h3 className="text-lg font-semibold mb-4 text-center">Lighting Effects</h3>
      <p className="text-gray-600 text-center mb-6">
        See how your blinds look in different lighting conditions
      </p>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {lightingOptions.map((lighting) => (
          <div
            key={lighting.id}
            onClick={() => handleLightingChange(lighting.id)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedLighting === lighting.id
                ? 'border-blue-500 bg-blue-50 shadow-lg'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
            }`}
          >
            <div className="text-center">
              <div className="text-2xl mb-2">{lighting.icon}</div>
              <h4 className="font-semibold text-gray-800 mb-1">{lighting.name}</h4>
              <p className="text-xs text-gray-600">{lighting.description}</p>
            </div>
          </div>
        ))}
      </div>

      {selectedLighting && (
        <div className="mt-4 p-3 bg-gray-50 rounded text-center">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Current:</span> {lightingOptions.find(l => l.id === selectedLighting)?.effect}
          </p>
        </div>
      )}
    </div>
  );
} 