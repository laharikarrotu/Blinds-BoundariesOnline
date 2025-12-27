// import { useAuth0 } from '@auth0/auth0-react'; // Disabled until Auth0 is configured

export default function LogoutButton() {
  // Temporarily disabled - Auth0 not configured
  // const { logout, isAuthenticated, user } = useAuth0();
  // if (!isAuthenticated) {
  //   return null;
  // }

  return (
    <button
      onClick={() => alert('Auth0 not configured. Please set up Auth0 to enable logout.')}
      className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
    >
      Log Out
    </button>
  );
} 