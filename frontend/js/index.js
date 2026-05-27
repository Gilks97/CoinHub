/**
 * CoinHub — Index Page
 * Fetches coin types from the API and renders the app selection grid.
 */

const loadingState = document.getElementById('loadingState');
const errorState   = document.getElementById('errorState');
const appGrid      = document.getElementById('appGrid');

async function loadApps() {
  loadingState.classList.remove('hidden');
  errorState.classList.add('hidden');
  appGrid.innerHTML = '';

  try {
    const coins = await API.getCoins();

    loadingState.classList.add('hidden');

    if (!coins.length) {
      errorState.innerHTML = '<p>No apps available right now. Please check back later.</p>';
      errorState.classList.remove('hidden');
      return;
    }

    coins.forEach((coin, i) => {
      const card = document.createElement('a');
      card.href = `recharge.html?app=${encodeURIComponent(coin.slug)}`;
      card.className = 'app-card';
      card.style.animationDelay = `${i * 40}ms`;

      // Icon: use backend icon_url, then local icons/, then placeholder initial
      const iconSrc = coin.icon_url || `icons/${coin.slug}.png`;
      const initial = coin.name.charAt(0).toUpperCase();

      card.innerHTML = `
        <img
          class="app-card-img"
          src="${iconSrc}"
          alt="${coin.name}"
          onerror="this.outerHTML='<div class=\\'app-card-img-placeholder\\'>${initial}</div>'"
        />
        <span class="app-card-name">${coin.name}</span>
      `;

      appGrid.appendChild(card);
    });

  } catch (err) {
    loadingState.classList.add('hidden');
    errorState.classList.remove('hidden');
    console.error('Failed to load coins:', err);
  }
}

document.addEventListener('DOMContentLoaded', loadApps);
