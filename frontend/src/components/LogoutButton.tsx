import { useAuth0 } from '@auth0/auth0-react';

export default function LogoutButton() {
  const { logout, isAuthenticated, user } = useAuth0();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        {user?.picture && (
          <img
            src={user.picture}
            alt={user.name || 'User'}
            className="w-8 h-8 rounded-full"
          />
        )}
        <span className="text-white font-medium">{user?.name || user?.email}</span>
      </div>
      <button
        onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
      >
        Log Out
      </button>
    </div>
  );
} 