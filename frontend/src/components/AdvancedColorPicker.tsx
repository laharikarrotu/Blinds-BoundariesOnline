import { useState } from 'react';

interface AdvancedColorPickerProps {
  selectedColor: string;
  onColorChange: (color: string) => void;
}

export default function AdvancedColorPicker({ selectedColor, onColorChange }: AdvancedColorPickerProps) {
  const [showCustomPicker, setShowCustomPicker] = useState(false);
  const [customColor, setCustomColor] = useState('#ffffff');

  const presetColors = [
    { name: 'White', value: '#ffffff' },
    { name: 'Cream', value: '#f5f5dc' },
    { name: 'Beige', value: '#f5f5dc' },
    { name: 'Light Gray', value: '#d3d3d3' },
    { name: 'Gray', value: '#808080' },
    { name: 'Dark Gray', value: '#404040' },
    { name: 'Light Brown', value: '#d2b48c' },
    { name: 'Brown', value: '#8b4513' },
    { name: 'Dark Brown', value: '#654321' },
    { name: 'Black', value: '#000000' },
    { name: 'Light Blue', value: '#add8e6' },
    { name: 'Blue', value: '#0000ff' },
    { name: 'Navy', value: '#000080' },
    { name: 'Light Green', value: '#90ee90' },
    { name: 'Green', value: '#008000' },
    { name: 'Dark Green', value: '#006400' },
    { name: 'Pink', value: '#ffc0cb' },
    { name: 'Red', value: '#ff0000' },
    { name: 'Orange', value: '#ffa500' },
    { name: 'Yellow', value: '#ffff00' },
    { name: 'Purple', value: '#800080' },
    { name: 'Lavender', value: '#e6e6fa' },
  ];

  const handleCustomColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const color = e.target.value;
    setCustomColor(color);
    onColorChange(color);
  };

  return (
    <div className="p-4 border border-gray-300 rounded-lg bg-white shadow">
      <h3 className="text-lg font-semibold mb-4">Advanced Color Selection</h3>
      
      {/* Preset Colors */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Preset Colors</h4>
        <div className="grid grid-cols-6 gap-2">
          {presetColors.map((color) => (
            <div key={color.value} className="flex flex-col items-center">
              <button
                onClick={() => onColorChange(color.value)}
                className={`w-10 h-10 rounded-full border-2 transition-all ${
                  selectedColor === color.value
                    ? 'border-blue-500 shadow-lg scale-110'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                style={{ backgroundColor: color.value }}
                title={color.name}
              >
                {selectedColor === color.value && (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                  </div>
                )}
              </button>
              <span className="text-xs text-gray-600 mt-1 text-center">{color.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Custom Color Picker */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium text-gray-700">Custom Color</h4>
          <button
            onClick={() => setShowCustomPicker(!showCustomPicker)}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            {showCustomPicker ? 'Hide' : 'Show'} Custom Picker
          </button>
        </div>
        
        {showCustomPicker && (
          <div className="flex items-center gap-4">
            <input
              type="color"
              value={customColor}
              onChange={handleCustomColorChange}
              className="w-16 h-16 border border-gray-300 rounded cursor-pointer"
            />
            <div className="flex-1">
              <input
                type="text"
                value={customColor}
                onChange={(e) => {
                  setCustomColor(e.target.value);
                  onColorChange(e.target.value);
                }}
                placeholder="#ffffff"
                className="w-full px-3 py-2 border border-gray-300 rounded text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter hex color code (e.g., #ff0000 for red)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Current Color Display */}
      <div className="flex items-center gap-3 p-3 bg-gray-50 rounded">
        <div
          className="w-8 h-8 rounded border border-gray-300"
          style={{ backgroundColor: selectedColor }}
        ></div>
        <div>
          <p className="text-sm font-medium">Selected Color</p>
          <p className="text-xs text-gray-600">{selectedColor}</p>
        </div>
      </div>
    </div>
  );
} 