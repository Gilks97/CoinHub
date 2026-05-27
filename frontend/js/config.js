/**
 * CoinHub Frontend Configuration
 * Set API_BASE to the backend URL in production.
 */
const CONFIG = {
  // In development (docker-compose): same origin via Nginx proxy → '/api'
  // In production: same. Override here if deploying separately.
  API_BASE: '/api',
  POLL_INTERVAL_MS: 3000,
  POLL_MAX_ATTEMPTS: 20,  // 20 × 3s = 60 seconds max
};
