/**
 * CoinHub Frontend Configuration
 * Dynamically switches backend URL based on environment.
 */
const CONFIG = {
  // If running locally on localhost/127.0.0.1, fall back to relative path '/api' (Nginx proxy)
  // In production, point directly to your Render backend service URL.
  API_BASE: window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? '/api' 
    : 'https://coinhub-backend.onrender.com/api', // <-- Replace with your actual Render URL later
    
  POLL_INTERVAL_MS: 3000,
  POLL_MAX_ATTEMPTS: 20,  
};
