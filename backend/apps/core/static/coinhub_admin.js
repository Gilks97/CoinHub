/* CoinHub admin: tap to copy values in changelist tables.
   Long-press still works natively because the cells use user-select: all. */
(function () {
  // Columns made copyable. Django adds the class "field-<column name>" to each cell.
  // Add more later, e.g. 'mpesa_receipt', 'phone_number'.
  var COPY_FIELDS = ['app_user_id'];

  // Small "Copied" message at the bottom of the screen
  function showToast(msg) {
    var t = document.querySelector('.ch-toast');
    if (!t) {
      t = document.createElement('div');
      t.className = 'ch-toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(function () { t.classList.remove('show'); }, 1500);
  }

  // Modern clipboard API (needs HTTPS, which Render provides),
  // with a textarea fallback for older browsers
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy') ? resolve() : reject(); }
      catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  // Mark the cells as copyable
  function enhance() {
    COPY_FIELDS.forEach(function (name) {
      document.querySelectorAll('#result_list td.field-' + name).forEach(function (td) {
        var value = td.textContent.trim();
        if (!value || value === '-') return;
        td.classList.add('ch-copy');
        td.setAttribute('data-copy', value);
        td.title = 'Tap to copy';
      });
    });
  }

  // One click listener for the whole page
  document.addEventListener('click', function (e) {
    var td = e.target.closest('td.ch-copy');
    if (!td) return;
    var value = td.getAttribute('data-copy');
    copyText(value)
      .then(function () { showToast('Copied: ' + value); })
      .catch(function () { showToast('Could not copy. Long-press to select instead.'); });
  });

  document.addEventListener('DOMContentLoaded', enhance);
})();