// import { useAuth0 } from '@auth0/auth0-react'; // Disabled until Auth0 is configured

export default function LoginButton() {
  // Temporarily disabled - Auth0 not configured
  // const { loginWithRedirect, isAuthenticated } = useAuth0();
  // if (isAuthenticated) {
  //   return null;
  // }

  return (
    <button
      onClick={() => alert('Auth0 not configured. Please set up Auth0 to enable login.')}
      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
    >
      Log In
    </button>
  );
} 