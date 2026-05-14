const menuButton = document.querySelector('.menu-btn');
const nav = document.querySelector('.nav');
menuButton?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});

document.querySelectorAll('[data-preview-form]').forEach((form) => {
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const note = form.querySelector('.form-note');
    if (note) note.textContent = 'Preview-режим: заявка не отправлена. Для запуска подключим CRM, почту или Telegram.';
  });
});

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', () => {
    nav?.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});
