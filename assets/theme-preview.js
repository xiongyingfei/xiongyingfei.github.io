/* Optional preview only. The default site works without JavaScript.
   No persistent storage: the chosen preview travels in internal HTML links. */
(() => {
  const theme = new URLSearchParams(location.search).get('theme');
  if (!['garden', 'classic', 'editorial', 'minimal'].includes(theme)) return;
  const sheet = document.getElementById('site-theme');
  sheet.href = `/assets/themes/${theme}.css?v=${sheet.dataset.revision || ''}`;
  document.querySelectorAll('a[href]').forEach(link => {
    const url = new URL(link.href, location.href);
    if (url.origin === location.origin && url.pathname.endsWith('.html') && !url.searchParams.has('theme')) {
      url.searchParams.set('theme', theme);
      link.href = url.href;
    }
  });
})();
