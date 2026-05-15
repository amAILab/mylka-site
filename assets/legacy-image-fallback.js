(function(){
  var map=[
    [/vakuum|nasos|kamera/i,'vacuum.svg'],[/silikon|mold|silicone/i,'silicone.svg'],[/poliuretan|poly|ure/i,'polyurethane.svg'],[/epoks|epoxy|smol/i,'epoxy.svg'],[/plastik|plastic/i,'liquid-plastic.svg'],[/pigment|krasitel|dobav|glitter|pudr/i,'additives.svg'],[/gips|beton|cement/i,'akril-gips.svg'],[/adgez|bond|poxy|glue|kle/i,'adgezivy.svg'],[/foamiran/i,'foamiran.svg'],[/penopoliuretan|foam/i,'foam-polyurethane.svg'],[/razdel|germetik|release/i,'release-agents.svg'],[/3d|pechat/i,'printing3d.svg'],[/svar/i,'welding.svg']
  ];
  function pick(img){
    var hay=((img.getAttribute('src')||'')+' '+(img.getAttribute('alt')||'')+' '+location.pathname).toLowerCase();
    for(var i=0;i<map.length;i++){ if(map[i][0].test(hay)) return map[i][1]; }
    return 'mylco-materials.svg';
  }
  function base(){
    var depth=location.pathname.replace(/^\/mylka-site\/?/,'').split('/').filter(Boolean).length-1;
    if(depth<0) depth=0;
    return new Array(depth+1).join('../')+'assets/visuals/';
  }
  function fallback(img){
    if(img.dataset.fallbackApplied) return;
    img.dataset.fallbackApplied='1';
    img.src=base()+pick(img);
    img.style.objectFit='cover';
    img.style.background='#eef4fb';
  }
  document.addEventListener('error',function(e){
    var t=e.target;
    if(t && t.tagName==='IMG') fallback(t);
  },true);
  document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll('img').forEach(function(img){
      if(!img.complete || img.naturalWidth===0) fallback(img);
    });
  });
})();
