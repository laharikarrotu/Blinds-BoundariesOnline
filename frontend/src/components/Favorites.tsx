import { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { databaseService, Favorite } from '../services/database';

// Function to save a favorite (exported for use in other components)
export const saveFavorite = async (
  imageId: string, 
  blindName: string, 
  blindType: string | undefined,
  color: string, 
  material: string | undefined,
  resultUrl: string,
  userId: string
) => {
  try {
    await databaseService.addFavorite({
      userId,
      imageId,
      blindName,
      blindType,
      color,
      material,
      resultUrl
    });
    return true;
  } catch (err) {
    console.error('Failed to save favorite:', err);
    throw new Error('Failed to save favorite');
  }
};

export default function Favorites() {
  const { isAuthenticated, user } = useAuth0();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user?.sub) {
      fetchFavorites();
    }
  }, [isAuthenticated, user?.sub]);

  const fetchFavorites = async () => {
    if (!user?.sub) return;
    
    setLoading(true);
    setError(null);

    try {
      const userFavorites = await databaseService.getFavorites(user.sub);
      setFavorites(userFavorites);
    } catch (err) {
      console.error('Failed to fetch favorites:', err);
      setError('Failed to load favorites');
    } finally {
      setLoading(false);
    }
  };

  const deleteFavorite = async (favoriteId: string) => {
    try {
      await databaseService.removeFavorite(favoriteId);
      // Refresh favorites list
      fetchFavorites();
    } catch (err) {
      console.error('Failed to delete favorite:', err);
      setError('Failed to delete favorite');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
        <p className="text-yellow-800">Please log in to view your favorites</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-2 text-gray-600">Loading favorites...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Your Favorite Combinations</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-800 rounded text-center">
          ❌ {error}
        </div>
      )}

      {favorites.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No favorites yet. Try on some blinds to save your favorites!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {favorites.map((favorite) => (
            <div key={favorite.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <img
                src={favorite.resultUrl}
                alt="Favorite result"
                className="w-full h-48 object-cover rounded-lg mb-3"
              />
              <div className="space-y-2">
                <p className="font-semibold">{favorite.blindName}</p>
                {favorite.blindType && (
                  <p className="text-sm text-gray-600">Type: {favorite.blindType}</p>
                )}
                {favorite.material && (
                  <p className="text-sm text-gray-600">Material: {favorite.material}</p>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-sm">Color:</span>
                  <div
                    className="w-6 h-6 rounded border border-gray-300"
                    style={{ backgroundColor: favorite.color }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500">
                  {favorite.createdAt.toDate().toLocaleDateString()}
                </p>
                <div className="flex gap-2">
                  <a
                    href={favorite.resultUrl}
                    download
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    Download
                  </a>
                  <button
                    onClick={() => deleteFavorite(favorite.id)}
                    className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 