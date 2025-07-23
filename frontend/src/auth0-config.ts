export const auth0Config = {
  domain: import.meta.env.VITE_AUTH0_DOMAIN || "YOUR_AUTH0_DOMAIN.auth0.com",
  clientId: import.meta.env.VITE_AUTH0_CLIENT_ID || "YOUR_AUTH0_CLIENT_ID",
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: "YOUR_API_AUDIENCE", // Optional: if you have an API
  },
}; 