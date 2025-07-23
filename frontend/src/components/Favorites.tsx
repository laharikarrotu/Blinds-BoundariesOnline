import { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

interface Favorite {
  id: string;
  image_id: string;
  blind_name: string;
  color: string;
  result_url: string;
  created_at: string;
}

// Function to save a favorite (exported for use in other components)
export const saveFavorite = async (
  imageId: string, 
  blindName: string, 
  color: string, 
  resultUrl: string,
  getAccessTokenSilently: () => Promise<string>
) => {
  try {
    const token = await getAccessTokenSilently();
    const response = await fetch('http://localhost:8000/favorites', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        image_id: imageId,
        blind_name: blindName,
        color: color,
        result_url: resultUrl,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to save favorite');
    }

    return true;
  } catch (err) {
    throw new Error('Failed to save favorite');
  }
};

export default function Favorites() {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    }
  }, [isAuthenticated]);

  const fetchFavorites = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = await getAccessTokenSilently();
      const response = await fetch('http://localhost:8000/favorites', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch favorites');
      }

      const data = await response.json();
      setFavorites(data.favorites);
    } catch (err) {
      setError('Failed to load favorites');
    } finally {
      setLoading(false);
    }
  };



  const deleteFavorite = async (favoriteId: string) => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(`http://localhost:8000/favorites/${favoriteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete favorite');
      }

      // Refresh favorites list
      fetchFavorites();
    } catch (err) {
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
            <div key={favorite.id} className="border border-gray-200 rounded-lg p-4">
              <img
                src={favorite.result_url}
                alt="Favorite result"
                className="w-full h-48 object-cover rounded-lg mb-3"
              />
              <div className="space-y-2">
                <p className="font-semibold">{favorite.blind_name}</p>
                <div className="flex items-center gap-2">
                  <span>Color:</span>
                  <div
                    className="w-6 h-6 rounded border border-gray-300"
                    style={{ backgroundColor: favorite.color }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500">
                  {new Date(favorite.created_at).toLocaleDateString()}
                </p>
                <div className="flex gap-2">
                  <a
                    href={favorite.result_url}
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