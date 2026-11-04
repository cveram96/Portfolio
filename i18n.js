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

    // Update data-tooltip for elements with data-i18n-tooltip (strip title to avoid native double tooltip)
    document.querySelectorAll('[data-i18n-tooltip]').forEach((el) => {
      const key = el.getAttribute('data-i18n-tooltip');
      if (dict[key] !== undefined) {
        el.setAttribute('data-tooltip', dict[key]);
      }
      el.removeAttribute('title');
    });

    // Strip title from all interactive and tooltip targets to permanently prevent native double tooltips
    document.querySelectorAll('.help-pill, [data-tooltip], [data-i18n-tooltip], input[type="range"]').forEach((el) => {
      el.removeAttribute('title');
    });

    // Update html lang attribute
    document.documentElement.setAttribute('lang', lang);

    // Update code comments & syntax highlighting for active language
    updateCodeComments(lang);

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
        <svg class="lang-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
        <button type="button" class="lang-pill-btn" data-lang="en" aria-label="Switch to English">EN</button>
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

    // ===== GLOBAL FLOATING TOOLTIP PORTAL =====
  function initTooltipPortal() {
    let portal = document.getElementById('globalTooltipPortal');
    if (!portal) {
      portal = document.createElement('div');
      portal.id = 'globalTooltipPortal';
      portal.className = 'global-tooltip-portal';
      portal.setAttribute('role', 'tooltip');
      portal.setAttribute('aria-hidden', 'true');
      document.body.appendChild(portal);
    }

    let activeTarget = null;

    function showTooltip(target) {
      let curr = target;
      while (curr && curr !== document.body) {
        curr.removeAttribute('title');
        curr = curr.parentElement;
      }
      const text = target.getAttribute('data-tooltip');
      if (!text) return;

      activeTarget = target;
      portal.textContent = text;
      portal.classList.add('visible');
      portal.setAttribute('aria-hidden', 'false');

      positionTooltip(target);
    }

    function hideTooltip(target) {
      if (activeTarget === target || !target) {
        portal.classList.remove('visible');
        portal.setAttribute('aria-hidden', 'true');
        if (target) target.removeAttribute('title');
        activeTarget = null;
      }
    }

    function positionTooltip(target) {
      if (!target || !portal.classList.contains('visible')) return;

      const rect = target.getBoundingClientRect();
      const tipRect = portal.getBoundingClientRect();
      const margin = 8;
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Clamped horizontal position
      let left = rect.left + (rect.width / 2) - (tipRect.width / 2);
      const minLeft = 12;
      const maxLeft = viewportWidth - tipRect.width - 12;
      left = Math.max(minLeft, Math.min(maxLeft, left));

      // Smart vertical flip
      let top;
      let placement = 'top';
      const spaceAbove = rect.top;
      const spaceBelow = viewportHeight - rect.bottom;

      if (spaceAbove >= tipRect.height + margin + 10) {
        top = rect.top - tipRect.height - margin;
        placement = 'top';
      } else if (spaceBelow >= tipRect.height + margin + 10) {
        top = rect.bottom + margin;
        placement = 'bottom';
      } else {
        if (spaceAbove >= spaceBelow) {
          top = Math.max(10, rect.top - tipRect.height - margin);
          placement = 'top';
        } else {
          top = Math.min(viewportHeight - tipRect.height - 10, rect.bottom + margin);
          placement = 'bottom';
        }
      }

      portal.style.left = Math.round(left) + 'px';
      portal.style.top = Math.round(top) + 'px';
      portal.setAttribute('data-placement', placement);
      const arrowX = Math.max(12, Math.min(tipRect.width - 12, rect.left + (rect.width / 2) - left));
      portal.style.setProperty('--arrow-left', Math.round(arrowX) + 'px');
    }

    document.body.addEventListener('mouseenter', (e) => {
      const target = e.target.closest ? e.target.closest('.help-pill, [data-tooltip]') : null;
      if (target) showTooltip(target);
    }, true);

    document.body.addEventListener('mouseleave', (e) => {
      const target = e.target.closest ? e.target.closest('.help-pill, [data-tooltip]') : null;
      if (target) hideTooltip(target);
    }, true);

    document.body.addEventListener('focusin', (e) => {
      const target = e.target.closest ? e.target.closest('.help-pill, [data-tooltip]') : null;
      if (target) showTooltip(target);
    }, true);

    document.body.addEventListener('focusout', (e) => {
      const target = e.target.closest ? e.target.closest('.help-pill, [data-tooltip]') : null;
      if (target) hideTooltip(target);
    }, true);

    window.addEventListener('scroll', () => {
      if (activeTarget) positionTooltip(activeTarget);
    }, { passive: true });

    window.addEventListener('resize', () => {
      if (activeTarget) positionTooltip(activeTarget);
    }, { passive: true });
  }

  // ===== AUTOMATIC HIGH-CONTRAST CODE SYNTAX HIGHLIGHTER & BILINGUAL COMMENTS =====
  function highlightText(codeText) {
    let text = codeText;
    const strings = [];
    text = text.replace(/(['"])(?:(?!\1)[^\\]|\\.)*\1/g, (m) => {
      strings.push(m);
      return '___STRING_' + (strings.length - 1) + '___';
    });

    const comments = [];
    // Comments: -- or // or # followed by text (excluding DAX assignments like # Titles = and CLI flags like --build)
    text = text.replace(/((?:--[ \t]+|\/\/(?:[ \t]|$)|(?:^|\s)#[ \t]+(?![A-Za-z0-9_#% ]+\s*=))[^\n]*)/gm, (m) => {
      comments.push(m);
      return '___COMMENT_' + (comments.length - 1) + '___';
    });

    // DAX columns / brackets
    text = text.replace(/(\[[A-Za-z0-9_#% ]+\])/g, '<span class="hl-col">$1</span>');

    // Keywords
    const kwRegex = /\b(SELECT|FROM|WHERE|JOIN|INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL JOIN|CROSS JOIN|ON|GROUP BY|ORDER BY|LIMIT|WITH|AS|AND|OR|NOT|IN|BETWEEN|LIKE|IS|NULL|CASE|WHEN|THEN|ELSE|END|HAVING|UNION|ALL|EXISTS|DISTINCT|OVER|PARTITION BY|CREATE|INDEX|EXPLAIN|QUERY|PLAN|DESC|ASC|VAR|RETURN|TRUE|FALSE)\b/gi;
    text = text.replace(kwRegex, (m) => '<span class="hl-kw">' + m.toUpperCase() + '</span>');

    // Functions
    const fnRegex = /\b(COUNT|SUM|AVG|MIN|MAX|ROUND|CAST|strftime|DENSE_RANK|LAG|LEAD|NTILE|ROW_NUMBER|COALESCE|IFNULL|CALCULATE|FILTER|ALL|ALLEXCEPT|DISTINCTCOUNT|DIVIDE|AVERAGE|FORMAT|SWITCH|RELATED|VALUES|USERELATIONSHIP|KEEPFILTERS)\b/gi;
    text = text.replace(fnRegex, (m) => '<span class="hl-fn">' + m + '</span>');

    // Numbers
    text = text.replace(/\b(\d+(?:\.\d+)?%?)\b/g, '<span class="hl-num">$1</span>');

    // Restore Strings & Comments
    text = text.replace(/___STRING_(\d+)___/g, (_, idx) => '<span class="hl-str">' + strings[Number(idx)] + '</span>');
    text = text.replace(/___COMMENT_(\d+)___/g, (_, idx) => '<span class="hl-cm">' + comments[Number(idx)] + '</span>');

    return text;
  }

  function updateCodeComments(lang) {
    const codeBlocks = document.querySelectorAll('pre code');
    if (!codeBlocks.length) return;

    const trans = window.translations || (typeof translations !== 'undefined' ? translations : null);
    const commentMap = (trans && trans.codeComments) || (typeof codeCommentTranslations !== 'undefined' ? codeCommentTranslations : null);

    codeBlocks.forEach((codeEl) => {
      if (!codeEl._rawTemplate) {
        codeEl._rawTemplate = codeEl.textContent;
      }
      let codeText = codeEl._rawTemplate;

      if (commentMap) {
        for (const [enKey, localized] of Object.entries(commentMap)) {
          if (codeText.includes(enKey)) {
            const targetComment = (localized && localized[lang]) ? localized[lang] : enKey;
            codeText = codeText.split(enKey).join(targetComment);
          }
        }
      }

      codeEl.innerHTML = highlightText(codeText);
      codeEl.setAttribute('data-highlighted', 'true');
    });
  }

  function init() {
    injectFloatingToggle();
    initTooltipPortal();
    const currentLang = getCurrentLang();
    setLanguage(currentLang);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose setLanguage globally for programmatic access if needed
  window.setPortfolioLanguage = setLanguage;
})();
