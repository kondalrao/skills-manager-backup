document.addEventListener('DOMContentLoaded', function () {
  if (typeof mermaid === 'undefined') {
    return;
  }
  mermaid.initialize({
    startOnLoad: true,
    theme: 'neutral',
    securityLevel: 'loose',
    flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
    sequence: { useMaxWidth: true, wrap: true },
  });
  var page = document.body.getAttribute('data-page');
  if (page) {
    var link = document.querySelector('.doc-nav a[href="' + page + '"]');
    if (link) {
      link.classList.add('active');
    }
  }
});
