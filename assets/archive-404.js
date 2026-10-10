// Only known archived downloads are redirected. Unrelated typos remain a 404.
(() => {
  let path;
  try { path = decodeURIComponent(location.pathname).replace(/^\/+/, ''); }
  catch { return; }
  fetch('/assets/course-archive.json')
    .then(response => response.ok ? response.json() : null)
    .then(manifest => {
      if (!manifest || !Object.prototype.hasOwnProperty.call(manifest.files, path)) return;
      const target = manifest.files[path];
      if (typeof target !== 'string' || !target.startsWith('/course-archive/')) return;
      const theme = new URLSearchParams(location.search).get('theme');
      location.replace(target + (['garden','classic','editorial','minimal'].includes(theme) ? '?theme=' + theme : ''));
    }).catch(() => { /* Keep the explanatory 404 page when offline. */ });
})();
