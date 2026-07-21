function haptic(type) {
  if (navigator.vibrate) {
    var patterns = { light: 10, medium: 20, heavy: 30, success: [10, 50, 10], error: [50, 50, 50] };
    navigator.vibrate(patterns[type] || 10);
  }
}

document.addEventListener('htmx:afterRequest', function (e) {
  if (e.detail.successful) {
    haptic('light');
  } else if (!e.detail.successful && e.detail.xhr && e.detail.xhr.status >= 400) {
    haptic('error');
  }
});
