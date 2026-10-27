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
const userIdError   = document.getElementById('userIdError');
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

// Turns what the user typed (7XX…, 07XX…, 2547XX…, +2547XX…) into the
// 9-digit national number, e.g. "712345678".
function getLocalPhone() {
  let d = phoneNumber.value.replace(/\D/g, '');   // keep digits only
  if (d.startsWith('254')) d = d.slice(3);        // drop country code if pasted
  if (d.startsWith('0'))   d = d.slice(1);        // drop leading 0 (07XX…)
  return d.slice(0, 9);
}

// Full number sent to the API, same format as before: 254 + 9 digits
function getFullPhone() {
  return '254' + getLocalPhone();
}

function validateStep1() {
  const hasId    = /^\d{1,10}$/.test(appUserId.value.trim());
  const hasPhone = /^[17]\d{8}$/.test(getLocalPhone());
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

let errorTimeout = null;

appUserId.addEventListener('input', (e) => {
  // Check if they typed anything that isn't a digit
  if (/[^0-9]/.test(e.target.value)) {
    // Show the warning message
    userIdError.style.display = 'block';
    
    // Clear any existing timer so it doesn't vanish early
    if (errorTimeout) clearTimeout(errorTimeout);
    
    // Hide the message automatically after 1.5 seconds
    errorTimeout = setTimeout(() => {
      userIdError.style.display = 'none';
    }, 1500);
  }

  // Strip out the non-numeric characters instantly
  e.target.value = e.target.value.replace(/[^0-9]/g, '');
  validateStep1();
});


// CHANGED: sanitize the phone field while typing.
// Digits only; the length cap depends on how the user started the number:
//   7XXXXXXXX (9) | 07XXXXXXXX (10) | 2547XXXXXXXX (12)
phoneNumber.addEventListener('input', (e) => {
  const digits = e.target.value.replace(/\D/g, '');
  const maxLen = digits.startsWith('254') ? 12 : digits.startsWith('0') ? 10 : 9;
  e.target.value = digits.slice(0, maxLen);
  validateStep1();
});


// ── Step 1 → Step 2 ──────────────────────────────────────────────────────────
btnNext.addEventListener('click', () => {
  const coins = parseInt(coinQty.value);
  const kes   = calcKes(coins);
  const phone = getFullPhone();

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
  const phone = getFullPhone();

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
