(function () {
  var cfg = window.RG_CONFIG || {};

  // шапка: граница при прокрутке
  var header = document.querySelector('.header');
  function onScroll() { header && header.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // бургер
  var burger = document.querySelector('.burger');
  var mnav = document.querySelector('.mobile-nav');
  if (burger && mnav) {
    burger.addEventListener('click', function () {
      var open = mnav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open);
      document.body.style.overflow = open ? 'hidden' : '';
    });
    mnav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { mnav.classList.remove('is-open'); burger.setAttribute('aria-expanded', false); document.body.style.overflow = ''; }
    });
  }

  // выпадающее меню «Услуги» по клику/клавиатуре
  document.querySelectorAll('.nav__drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var d = b.parentElement, open = d.classList.toggle('is-open');
      b.setAttribute('aria-expanded', open);
    });
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.nav__drop.is-open').forEach(function (d) {
      if (!d.contains(e.target)) { d.classList.remove('is-open'); d.querySelector('button').setAttribute('aria-expanded', false); }
    });
  });

  // UTM и источник — сохраняем на сессию, чтобы передать в заявку
  var params = new URLSearchParams(location.search), utm = {};
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid'].forEach(function (k) {
    if (params.get(k)) utm[k] = params.get(k);
  });
  try {
    if (Object.keys(utm).length) sessionStorage.setItem('rg_utm', JSON.stringify(utm));
    else utm = JSON.parse(sessionStorage.getItem('rg_utm') || '{}');
    if (!sessionStorage.getItem('rg_ref')) sessionStorage.setItem('rg_ref', document.referrer || '');
  } catch (e) {}

  function goal(name) {
    try { if (window.ym && cfg.metrikaId) window.ym(cfg.metrikaId, 'reachGoal', name); } catch (e) {}
  }

  // клики по телефону и мессенджерам — цели Метрики
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a'); if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('tel:') === 0) goal('click_phone');
    else if (h.indexOf('t.me') > -1) goal('click_telegram');
    else if (h.indexOf('wa.me') > -1) goal('click_whatsapp');
  });

  // модалка заявки
  var modal = document.getElementById('lead-modal');
  document.querySelectorAll('[data-open-lead]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      if (!modal || !modal.showModal) return;
      e.preventDefault();
      var svc = b.getAttribute('data-service');
      if (svc) {
        var box = modal.querySelector('input[name="service[]"][value="' + svc + '"]');
        if (box) box.checked = true;
      }
      modal.showModal(); goal('open_form');
    });
  });
  if (modal) {
    modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); });
    modal.querySelector('.modal__close').addEventListener('click', function () { modal.close(); });
  }

  // отправка заявки
  document.querySelectorAll('form.lead-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.form-note'), btn = form.querySelector('button[type="submit"]');
      if (form.website && form.website.value) return; // ловушка для ботов
      var phone = (form.phone.value || '').replace(/\D/g, '');
      if (phone.length < 10) { note.textContent = 'Проверьте номер телефона.'; form.phone.focus(); return; }
      var data = new FormData(form);
      data.append('page', location.pathname);
      data.append('page_title', document.title);
      try { data.append('referrer', sessionStorage.getItem('rg_ref') || ''); } catch (e2) {}
      Object.keys(utm).forEach(function (k) { data.append(k, utm[k]); });
      btn.disabled = true; note.textContent = 'Отправляем…';
      fetch(cfg.formEndpoint || 'send.php', { method: 'POST', body: data })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r; })
        .then(function () {
          goal('lead');
          form.reset();
          note.textContent = 'Заявка принята. Ответим в течение рабочего часа.';
          if (cfg.thanksPage) location.href = cfg.thanksPage;
        })
        .catch(function () {
          note.innerHTML = 'Не получилось отправить. Напишите нам: <a href="' + (cfg.telegram || '#') + '">Telegram</a> или позвоните <a href="tel:' + (cfg.phoneRaw || '') + '">' + (cfg.phone || '') + '</a>.';
        })
        .finally(function () { btn.disabled = false; });
    });
  });

  // маска телефона: +7 (___) ___-__-__
  document.querySelectorAll('input[type="tel"]').forEach(function (inp) {
    inp.addEventListener('input', function () {
      var d = inp.value.replace(/\D/g, '');
      if (d[0] === '8') d = '7' + d.slice(1);
      if (d && d[0] !== '7') d = '7' + d;
      d = d.slice(0, 11);
      var o = d ? '+7' : '';
      if (d.length > 1) o += ' (' + d.slice(1, 4);
      if (d.length >= 4) o += ') ' + d.slice(4, 7);
      if (d.length >= 7) o += '-' + d.slice(7, 9);
      if (d.length >= 9) o += '-' + d.slice(9, 11);
      inp.value = o;
    });
  });
})();
