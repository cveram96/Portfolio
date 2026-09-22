/**
 * i18n.js
 * Internationalization controller for Christian Vera's Portfolio.
 * Default language: English ('en').
 * Features:
 * - Injects sleek floating language toggle button in top right corner.
 * - Reactive translation without page refresh.
 * - Persistent language preference via localStorage.
 */

(function () {
  const STORAGE_KEY = 'portfolio_lang';
  const DEFAULT_LANG = 'en';

  function getCurrentLang() {
    return localStorage.getItem(STORAGE_KEY) || DEFAULT_LANG;
  }

  function setLanguage(lang) {
    const trans = window.translations || (typeof translations !== 'undefined' ? translations : null);
    if (!trans || !trans[lang]) {
      console.warn(`[i18n] Translations not found for language: ${lang}`);
      return;
    }

    const dict = trans[lang];

    // Update textContent for elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Update innerHTML for elements with data-i18n-html (for bold, links, etc.)
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
      const key = el.getAttribute('data-i18n-html');
      if (dict[key] !== undefined) {
        el.innerHTML = dict[key];
      }
    });

    // Update html lang attribute
    document.documentElement.setAttribute('lang', lang);

    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, lang);

    // Update toggle button active states
    updateToggleUI(lang);
  }

  function updateToggleUI(activeLang) {
    const toggle = document.getElementById('floatingLangToggle');
    if (!toggle) return;

    toggle.querySelectorAll('.lang-pill-btn').forEach((btn) => {
      const btnLang = btn.getAttribute('data-lang');
      if (btnLang === activeLang) {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
      }
    });
  }

  function injectFloatingToggle() {
    if (document.getElementById('floatingLangToggle')) return;

    const toggleWrapper = document.createElement('div');
    toggleWrapper.id = 'floatingLangToggle';
    toggleWrapper.className = 'lang-toggle-floating';
    toggleWrapper.setAttribute('role', 'region');
    toggleWrapper.setAttribute('aria-label', 'Language Switcher');

    toggleWrapper.innerHTML = `
      <div class="lang-toggle-inner">
        <span class="lang-icon" aria-hidden="true">🌐</span>
        <button type="button" class="lang-pill-btn" data-lang="en" aria-label="Switch to English">EN</button>
        <span class="lang-sep">/</span>
        <button type="button" class="lang-pill-btn" data-lang="es" aria-label="Cambiar a Español">ES</button>
      </div>
    `;

    document.body.appendChild(toggleWrapper);

    // Attach click events
    toggleWrapper.querySelectorAll('.lang-pill-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const targetLang = btn.getAttribute('data-lang');
        setLanguage(targetLang);
      });
    });

    updateToggleUI(getCurrentLang());
  }

  function init() {
    injectFloatingToggle();
    const currentLang = getCurrentLang();
    // Only apply if translations exist and language is different or to ensure synced DOM
    if (currentLang !== 'en') {
      setLanguage(currentLang);
    } else {
      updateToggleUI('en');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose setLanguage globally for programmatic access if needed
  window.setPortfolioLanguage = setLanguage;
})();
