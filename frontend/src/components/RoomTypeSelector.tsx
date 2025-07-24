

interface RoomTypeSelectorProps {
  selectedRoom: string;
  onRoomChange: (room: string) => void;
}

export default function RoomTypeSelector({ selectedRoom, onRoomChange }: RoomTypeSelectorProps) {
  const roomTypes = [
    {
      id: 'living-room',
      name: 'Living Room',
      description: 'Comfortable and stylish blinds for your main living space',
      icon: '🏠',
      recommendedBlinds: ['image1.jpeg', 'image2.jpeg', 'image3.jpeg']
    },
    {
      id: 'bedroom',
      name: 'Bedroom',
      description: 'Privacy-focused blinds for restful sleep',
      icon: '🛏️',
      recommendedBlinds: ['image2.jpeg', 'image4.jpeg', 'image5.jpeg']
    },
    {
      id: 'kitchen',
      name: 'Kitchen',
      description: 'Easy-to-clean blinds for cooking areas',
      icon: '🍳',
      recommendedBlinds: ['image1.jpeg', 'image3.jpeg', 'image5.jpeg']
    },
    {
      id: 'bathroom',
      name: 'Bathroom',
      description: 'Moisture-resistant blinds for bathrooms',
      icon: '🚿',
      recommendedBlinds: ['image4.jpeg', 'image5.jpeg']
    },
    {
      id: 'home-office',
      name: 'Home Office',
      description: 'Professional blinds for productivity',
      icon: '💼',
      recommendedBlinds: ['image1.jpeg', 'image2.jpeg', 'image3.jpeg']
    },
    {
      id: 'dining-room',
      name: 'Dining Room',
      description: 'Elegant blinds for formal dining spaces',
      icon: '🍽️',
      recommendedBlinds: ['image2.jpeg', 'image3.jpeg', 'image4.jpeg']
    },
    {
      id: 'nursery',
      name: 'Nursery',
      description: 'Safe and gentle blinds for children',
      icon: '👶',
      recommendedBlinds: ['image1.jpeg', 'image2.jpeg']
    },
    {
      id: 'other',
      name: 'Other',
      description: 'Custom blinds for any space',
      icon: '🏡',
      recommendedBlinds: ['image1.jpeg', 'image2.jpeg', 'image3.jpeg', 'image4.jpeg', 'image5.jpeg']
    }
  ];

  return (
    <div className="p-6 border border-gray-300 rounded-lg max-w-4xl mx-auto mt-8 bg-white shadow">
      <h3 className="text-xl font-semibold mb-6 text-center">Choose Your Room Type</h3>
      <p className="text-gray-600 text-center mb-6">
        Select your room type to get personalized blind recommendations
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {roomTypes.map((room) => (
          <div
            key={room.id}
            onClick={() => onRoomChange(room.id)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              selectedRoom === room.id
                ? 'border-blue-500 bg-blue-50 shadow-lg'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
            }`}
          >
            <div className="text-center">
              <div className="text-3xl mb-2">{room.icon}</div>
              <h4 className="font-semibold text-gray-800 mb-1">{room.name}</h4>
              <p className="text-xs text-gray-600 mb-3">{room.description}</p>
              
              {selectedRoom === room.id && (
                <div className="mt-3 p-2 bg-blue-100 rounded">
                  <p className="text-xs font-medium text-blue-800 mb-1">Recommended:</p>
                  <div className="flex justify-center gap-1">
                    {room.recommendedBlinds.slice(0, 3).map((blind, index) => (
                      <div
                        key={index}
                        className="w-6 h-6 bg-gray-200 rounded text-xs flex items-center justify-center"
                        title={blind}
                      >
                        {index + 1}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {selectedRoom && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-800 mb-2">
            💡 Tips for {roomTypes.find(r => r.id === selectedRoom)?.name}
          </h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {selectedRoom === 'living-room' && (
              <>
                <li>• Choose light-filtering blinds for natural light</li>
                <li>• Consider motorized options for convenience</li>
                <li>• Match your existing decor color scheme</li>
              </>
            )}
            {selectedRoom === 'bedroom' && (
              <>
                <li>• Opt for blackout blinds for better sleep</li>
                <li>• Choose noise-reducing materials</li>
                <li>• Consider easy-to-clean fabrics</li>
              </>
            )}
            {selectedRoom === 'kitchen' && (
              <>
                <li>• Select moisture-resistant materials</li>
                <li>• Choose easy-to-clean options</li>
                <li>• Consider heat-resistant fabrics</li>
              </>
            )}
            {selectedRoom === 'bathroom' && (
              <>
                <li>• Use moisture-resistant blinds</li>
                <li>• Choose privacy-focused designs</li>
                <li>• Consider easy maintenance</li>
              </>
            )}
            {selectedRoom === 'home-office' && (
              <>
                <li>• Select light-filtering for productivity</li>
                <li>• Choose professional-looking styles</li>
                <li>• Consider glare reduction</li>
              </>
            )}
            {selectedRoom === 'dining-room' && (
              <>
                <li>• Choose elegant, formal styles</li>
                <li>• Consider light control for ambiance</li>
                <li>• Match your dining furniture</li>
              </>
            )}
            {selectedRoom === 'nursery' && (
              <>
                <li>• Select child-safe materials</li>
                <li>• Choose gentle light filtering</li>
                <li>• Consider easy operation</li>
              </>
            )}
            {selectedRoom === 'other' && (
              <>
                <li>• Consider your specific needs</li>
                <li>• Think about maintenance requirements</li>
                <li>• Match your overall design theme</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
} 