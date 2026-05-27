/**
 * CoinHub — Recharge Page
 *
 * Multi-step flow:
 *   Step 1: User inputs (App User ID, phone, coin qty) + live KES preview
 *   Step 2: Confirmation summary before payment
 *   Step 3: Processing → poll status → success / fail
 */

// ── State ────────────────────────────────────────────────────────────────────
let currentCoin = null;   // CoinType object from API
let currentRef  = null;   // CoinHub order reference after POST /recharges/
let pollTimer   = null;
let pollCount   = 0;

// ── DOM refs ─────────────────────────────────────────────────────────────────
const appIcon       = document.getElementById('appIcon');
const appName       = document.getElementById('appName');
const appUserId     = document.getElementById('appUserId');
const phoneNumber   = document.getElementById('phoneNumber');
const coinQty       = document.getElementById('coinQty');
const kesAmount     = document.getElementById('kesAmount');
const btnNext       = document.getElementById('btnNext');
const btnBack       = document.getElementById('btnBack');
const btnPay        = document.getElementById('btnPay');
const btnRetry      = document.getElementById('btnRetry');

const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const steps = document.querySelectorAll('.step');
const stepLines = document.querySelectorAll('.step-line');

const stateProcessing = document.getElementById('stateProcessing');
const stateSuccess    = document.getElementById('stateSuccess');
const stateFailed     = document.getElementById('stateFailed');

const pollBarFill = document.getElementById('pollBarFill');
const pollHint    = document.getElementById('pollHint');

// ── Helpers ───────────────────────────────────────────────────────────────────
function showPanel(panelEl) {
  [step1, step2, step3].forEach(p => p.classList.add('hidden'));
  panelEl.classList.remove('hidden');
}

function setActiveStep(n) {
  steps.forEach((s, i) => {
    const num = i + 1;
    s.classList.remove('active', 'done');
    if (num < n) s.classList.add('done');
    if (num === n) s.classList.add('active');
  });
  stepLines.forEach((l, i) => {
    l.classList.toggle('done', i + 1 < n);
  });
}

function calcKes(coins) {
  if (!currentCoin || !coins || coins <= 0) return 0;
  return Math.ceil(coins / parseFloat(currentCoin.conversion_rate));
}

function formatKes(n) {
  return n.toLocaleString('en-KE');
}

function validateStep1() {
  const hasId    = appUserId.value.trim().length > 0;
  const hasPhone = /^\d{9}$/.test(phoneNumber.value.trim());
  const hasCoins = parseInt(coinQty.value) > 0;
  btnNext.disabled = !(hasId && hasPhone && hasCoins);
}

// ── Init: load coin from API ──────────────────────────────────────────────────
async function init() {
  const params = new URLSearchParams(window.location.search);
  const slug   = params.get('app');

  if (!slug) {
    appName.textContent = 'Unknown App';
    return;
  }

  try {
    const coins = await API.getCoins();
    currentCoin = coins.find(c => c.slug === slug);

    if (!currentCoin) {
      appName.textContent = 'App Not Found';
      return;
    }

    // Populate identity strip
    appName.textContent = currentCoin.name;
    const iconSrc = currentCoin.icon_url || `icons/${currentCoin.slug}.png`;
    appIcon.src = iconSrc;
    appIcon.alt = currentCoin.name;
    appIcon.classList.remove('hidden');
    appIcon.onerror = () => appIcon.classList.add('hidden');

    document.title = `CoinHub — ${currentCoin.name} Recharge`;

  } catch (err) {
    appName.textContent = 'Could not load app data';
    console.error(err);
  }
}

// ── Live KES calculation ───────────────────────────────────────────────────────
function onCoinInput() {
  const coins = parseInt(coinQty.value) || 0;
  const kes   = calcKes(coins);
  kesAmount.textContent = formatKes(kes);
  validateStep1();
}

coinQty.addEventListener('input', onCoinInput);
appUserId.addEventListener('input', validateStep1);
phoneNumber.addEventListener('input', validateStep1);

// ── Step 1 → Step 2 ──────────────────────────────────────────────────────────
btnNext.addEventListener('click', () => {
  const coins = parseInt(coinQty.value);
  const kes   = calcKes(coins);
  const phone = '254' + phoneNumber.value.trim();

  document.getElementById('confApp').textContent     = currentCoin.name;
  document.getElementById('confUserId').textContent  = appUserId.value.trim();
  document.getElementById('confPhone').textContent   = `+${phone}`;
  document.getElementById('confCoins').textContent   = coins.toLocaleString();
  document.getElementById('confTotal').textContent   = `KES ${formatKes(kes)}`;

  showPanel(step2);
  setActiveStep(2);
});

// ── Step 2 → Step 1 (back) ────────────────────────────────────────────────────
btnBack.addEventListener('click', () => {
  showPanel(step1);
  setActiveStep(1);
});

// ── Step 2 → Step 3: Pay ──────────────────────────────────────────────────────
btnPay.addEventListener('click', async () => {
  showPanel(step3);
  setActiveStep(3);
  showResultState('processing');

  const coins = parseInt(coinQty.value);
  const phone = '254' + phoneNumber.value.trim();

  try {
    const result = await API.createRecharge({
      coin_type_slug:  currentCoin.slug,
      app_user_id:     appUserId.value.trim(),
      phone_number:    phone,
      coins_requested: coins,
    });

    currentRef = result.reference;
    startPolling();

  } catch (err) {
    console.error('Recharge failed:', err);
    let msg = 'Could not initiate payment.';
    if (err.data) {
      // Flatten DRF validation errors
      const errs = Object.values(err.data).flat();
      if (errs.length) msg = errs.join(' ');
    }
    showResultState('failed');
    document.querySelector('#stateFailed p').textContent = msg;
  }
});

// ── Retry ─────────────────────────────────────────────────────────────────────
btnRetry.addEventListener('click', () => {
  stopPolling();
  showPanel(step1);
  setActiveStep(1);
});

// ── Polling ───────────────────────────────────────────────────────────────────
function startPolling() {
  pollCount = 0;
  pollBarFill.style.width = '0%';
  pollHint.textContent = 'Waiting for confirmation…';
  poll();
}

function stopPolling() {
  if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }
}

async function poll() {
  if (!currentRef) return;
  pollCount++;

  const progress = Math.min((pollCount / CONFIG.POLL_MAX_ATTEMPTS) * 100, 95);
  pollBarFill.style.width = progress + '%';
  pollHint.textContent = `Checking… (${pollCount}/${CONFIG.POLL_MAX_ATTEMPTS})`;

  try {
    const data = await API.getPaymentStatus(currentRef);

    if (data.payment_status === 'success' || data.status === 'paid') {
      stopPolling();
      pollBarFill.style.width = '100%';
      document.getElementById('successRef').textContent     = data.reference || currentRef;
      document.getElementById('successReceipt').textContent = data.mpesa_receipt || 'Pending';
      document.getElementById('successMsg').textContent =
        `${data.coins_requested?.toLocaleString() || ''} ${currentCoin.name} coins queued for loading.`;
      showResultState('success');
      return;
    }

    if (data.payment_status === 'failed' || data.status === 'failed') {
      stopPolling();
      showResultState('failed');
      document.querySelector('#stateFailed p').textContent =
        'Your M-Pesa transaction was declined or timed out. Please try again.';
      return;
    }

  } catch (err) {
    console.warn('Poll error:', err);
  }

  if (pollCount >= CONFIG.POLL_MAX_ATTEMPTS) {
    stopPolling();
    showResultState('failed');
    document.querySelector('#stateFailed p').textContent =
      'Payment confirmation timed out. If your M-Pesa was charged, please contact support with reference: ' + currentRef;
    return;
  }

  pollTimer = setTimeout(poll, CONFIG.POLL_INTERVAL_MS);
}

function showResultState(state) {
  stateProcessing.classList.add('hidden');
  stateSuccess.classList.add('hidden');
  stateFailed.classList.add('hidden');

  if (state === 'processing') stateProcessing.classList.remove('hidden');
  if (state === 'success')    stateSuccess.classList.remove('hidden');
  if (state === 'failed')     stateFailed.classList.remove('hidden');
}

// ── Boot ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
