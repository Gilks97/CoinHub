/**
 * CoinHub API Client
 * Thin wrapper around fetch for all backend calls.
 */
const API = {

  /**
   * GET /api/coins/
   * Returns active coin types with rates.
   */
  async getCoins() {
    const res = await fetch(`${CONFIG.API_BASE}/coins/`);
    if (!res.ok) throw new Error(`Failed to load coins (${res.status})`);
    return res.json();
  },

  /**
   * POST /api/recharges/
   * Initiates the STK push and creates the order.
   */
  async createRecharge({ coin_type_slug, app_user_id, phone_number, coins_requested }) {
    const res = await fetch(`${CONFIG.API_BASE}/recharges/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ coin_type_slug, app_user_id, phone_number, coins_requested }),
    });
    const data = await res.json();
    if (!res.ok) throw { status: res.status, data };
    return data;
  },

  /**
   * GET /api/payment-status/<reference>/
   * Poll for payment result.
   */
  async getPaymentStatus(reference) {
    const res = await fetch(`${CONFIG.API_BASE}/payment-status/${reference}/`);
    if (!res.ok) throw new Error(`Status check failed (${res.status})`);
    return res.json();
  },
};
