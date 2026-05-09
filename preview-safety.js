(function(){
  var PREVIEW_MESSAGE='Форма в preview-режиме. Для заявки используйте телефон или e-mail, указанные на странице контактов.';
  function ready(fn){if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',fn);}else{fn();}}
  function addEvent(el,name){ if(el && !el.getAttribute('data-event')) el.setAttribute('data-event',name); }
  ready(function(){
    var main=document.querySelector('main,[role=\"main\"],#content,.mx-main,.content');
    if(main && !main.id){ main.id='main'; main.setAttribute('tabindex','-1'); }
    if(!document.querySelector('.skip-link')){
      var skip=document.createElement('a'); skip.className='skip-link'; skip.href=main ? '#'+main.id : '#content'; skip.textContent='Перейти к содержанию'; document.body.insertBefore(skip, document.body.firstChild);
    }
    if(!document.querySelector('.mylco-preview-banner')){
      var banner=document.createElement('div'); banner.className='mylco-preview-banner'; banner.setAttribute('role','status'); banner.innerHTML='<strong>Preview-прототип Mylco.</strong> Корзина, кабинет, checkout и формы не подключены к backend/CRM.'; document.body.insertBefore(banner, document.body.querySelector('.app')||document.body.firstChild);
    }
    document.querySelectorAll('a[href^="tel:"]').forEach(function(a){addEvent(a,'click_phone');});
    document.querySelectorAll('a[href^="mailto:"]').forEach(function(a){addEvent(a,'click_email'); if(/подбор|заявка|КП|quote/i.test(decodeURIComponent(a.href))){addEvent(a,'request_quote_click');}});
    document.querySelectorAll('a[href*="mylco.ru"]').forEach(function(a){a.classList.add('mylco-live-link'); a.setAttribute('data-live-link','mylco.ru'); if(!a.title) a.title='Ссылка ведёт на live-сайт mylco.ru';});
    document.querySelectorAll('a[href*="cart"],a[href*="checkout"],a[href*="simplecheckout"],a[href*="my-account"],a[href*="wishlist"],a[href*="compare-products"],a[href*="login"],a[href*="forgot-password"],a[href*="simpleregister"],button[class*="cart"],button[onclick*="cart."]').forEach(function(el){
      el.classList.add('mylco-preview-disabled'); el.setAttribute('aria-disabled','true'); el.setAttribute('data-preview-disabled','true'); if(!el.getAttribute('data-event')) el.setAttribute('data-event', el.href && el.href.indexOf('cart')>-1 ? 'add_to_cart' : 'preview_disabled_click');
    });
    document.addEventListener('click',function(e){
      var blocked=e.target.closest('[data-preview-disabled="true"], a[href*="cart"], a[href*="checkout"], a[href*="simplecheckout"], a[href*="my-account"], a[href*="wishlist"], a[href*="compare-products"]');
      if(blocked){ e.preventDefault(); alert('Эта функция отключена в preview. Для заказа используйте телефон или e-mail.'); }
    },true);
    document.querySelectorAll('form').forEach(function(form){
      if(!form.querySelector('.mylco-preview-form-note')){ var note=document.createElement('div'); note.className='mylco-preview-form-note'; note.textContent=PREVIEW_MESSAGE; form.appendChild(note); }
      form.querySelectorAll('input[name*="name" i]').forEach(function(i){i.setAttribute('autocomplete','name');});
      form.querySelectorAll('input[name*="phone" i],input[type="tel"]').forEach(function(i){i.setAttribute('autocomplete','tel');});
      form.querySelectorAll('input[name*="email" i],input[type="email"]').forEach(function(i){i.setAttribute('autocomplete','email');});
      form.querySelectorAll('input[name*="company" i],input[name*="organization" i]').forEach(function(i){i.setAttribute('autocomplete','organization');});
      form.addEventListener('submit',function(e){e.preventDefault(); alert(PREVIEW_MESSAGE);});
    });
  });
})();
