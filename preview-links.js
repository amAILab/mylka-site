(function(){
  var previewOrigin = 'https://amailab.github.io/mylka-site/';
  document.querySelectorAll('a[href]').forEach(function(link){
    var href = link.getAttribute('href');
    if (!href || !/^https?:\/\/mylco\.ru\/?/i.test(href)) return;
    try {
      var url = new URL(href);
      var localPath = url.pathname.replace(/^\//, '');
      if (!localPath) localPath = 'index.html';
      link.setAttribute('href', previewOrigin + localPath + url.search + url.hash);
    } catch (e) {}
  });
})();
