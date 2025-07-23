export const auth0Config = {
  domain: "YOUR_AUTH0_DOMAIN.auth0.com", // Replace with your Auth0 domain
  clientId: "YOUR_AUTH0_CLIENT_ID", // Replace with your Auth0 client ID
  authorizationParams: {
    redirect_uri: window.location.origin,
    audience: "YOUR_API_AUDIENCE", // Optional: if you have an API
  },
}; 