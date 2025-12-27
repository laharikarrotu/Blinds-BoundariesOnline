import { useState, useEffect } from 'react';
// import { useAuth0 } from '@auth0/auth0-react'; // Disabled until Auth0 is configured
import { databaseService, type History } from '../services/database';

export default function History() {
  // Temporarily disabled - Auth0 not configured
  // const { isAuthenticated, user } = useAuth0();
  const isAuthenticated = false;
  const user: { sub?: string } | null = null;
  const [history, setHistory] = useState<History[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user?.sub) {
      fetchHistory();
    }
  }, [isAuthenticated, user?.sub]);

  const fetchHistory = async () => {
    if (!user?.sub) return;
    
    setLoading(true);
    setError(null);

    try {
      const userHistory = await databaseService.getHistory(user.sub, 50);
      setHistory(userHistory);
    } catch (err) {
      console.error('Failed to fetch history:', err);
      setError('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    if (!user?.sub) return;
    
    if (window.confirm('Are you sure you want to clear all history? This action cannot be undone.')) {
      try {
        await databaseService.clearHistory(user.sub);
        setHistory([]);
      } catch (err) {
        console.error('Failed to clear history:', err);
        setError('Failed to clear history');
      }
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
        <p className="text-yellow-800">Please log in to view your history</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-8">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        <p className="mt-2 text-gray-600">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Your Try-On History</h2>
        {history.length > 0 && (
          <button
            onClick={clearHistory}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors text-sm"
          >
            Clear All
          </button>
        )}
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-800 rounded text-center">
          ❌ {error}
        </div>
      )}

      {history.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No history yet. Try on some blinds to see your history!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {history.map((item) => (
            <div key={item.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <img
                src={item.resultUrl}
                alt="History result"
                className="w-full h-48 object-cover rounded-lg mb-3"
              />
              <div className="space-y-2">
                <p className="font-semibold">{item.blindName}</p>
                {item.blindType && (
                  <p className="text-sm text-gray-600">Type: {item.blindType}</p>
                )}
                {item.material && (
                  <p className="text-sm text-gray-600">Material: {item.material}</p>
                )}
                <div className="flex items-center gap-2">
                  <span className="text-sm">Color:</span>
                  <div
                    className="w-6 h-6 rounded border border-gray-300"
                    style={{ backgroundColor: item.color }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500">
                  {item.createdAt.toDate().toLocaleDateString()} at {item.createdAt.toDate().toLocaleTimeString()}
                </p>
                <div className="flex gap-2">
                  <a
                    href={item.resultUrl}
                    download
                    className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    Download
                  </a>
                  <a
                    href={item.resultUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    View
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 