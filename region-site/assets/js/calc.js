/* Калькулятор стоимости маркетинга. Цены и средние по нишам — window.RG_PRICES (задаются в build.py). */
(function () {
  var P = window.RG_PRICES, root = document.getElementById('calc');
  if (!P || !root) return;

  var $ = function (s) { return root.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(root.querySelectorAll(s)); };
  var rub = function (n) { return Math.round(n).toLocaleString('ru-RU').replace(/,/g, ' ') + ' ₽'; };
  var round = function (n, step) { return Math.round(n / step) * step; };
  var val = function (name) { var el = root.querySelector('[name="' + name + '"]:checked') || root.querySelector('[name="' + name + '"]'); return el ? el.value : ''; };
  var on = function (name) { var el = root.querySelector('[name="' + name + '"]'); return !!(el && el.checked); };

  function tier(list, budget) {
    for (var i = 0; i < list.length; i++) if (budget <= list[i][0]) return list[i][1];
    return list[list.length - 1][1];
  }

  // предвыбор услуги из ?s=direct или #direct
  var pre = new URLSearchParams(location.search).get('s') || (location.hash || '').replace('#', '');
  if (pre && root.querySelector('[data-svc="' + pre + '"]')) {
    $$('[data-svc] > .calc-svc__head input').forEach(function (i) { i.checked = false; });
    root.querySelector('[data-svc="' + pre + '"] > .calc-svc__head input').checked = true;
  }

  function sync() {
    $$('[data-svc]').forEach(function (b) {
      var active = b.querySelector('.calc-svc__head input').checked;
      b.classList.toggle('is-on', active);
      b.querySelector('.calc-svc__opts').hidden = !active;
    });
    $$('input[type="range"]').forEach(function (r) {
      var out = root.querySelector('[data-out="' + r.name + '"]');
      if (out) out.textContent = rub(+r.value);
      r.style.setProperty('--fill', ((r.value - r.min) / (r.max - r.min) * 100) + '%');
    });
  }

  function calc() {
    sync();
    var niche = P.niches[val('niche')] || P.niches.other;
    var region = P.regions[val('region')] || P.regions.local;
    var check = Math.max(0, +(val('check') || 0));
    var monthly = 0, once = 0, ads = 0, leadsLo = 0, leadsHi = 0, count = 0, lines = [];

    if (on('svc_direct')) {
      var b = +val('direct_budget'), fee = tier(P.direct.fee, b), set = P.direct.setup + (on('direct_shop') ? P.direct.shopExtra : 0);
      monthly += fee; once += set; ads += b; count++;
      var l = b / (niche.cpl * region.cpl);
      leadsLo += l * 0.75; leadsHi += l * 1.25;
      lines.push(['Яндекс Директ', fee, set]);
    }
    if (on('svc_vk')) {
      var bv = +val('vk_budget'), feev = tier(P.vk.fee, bv);
      monthly += feev; once += P.vk.setup; ads += bv; count++;
      var lv = bv / (niche.cpl * region.cpl * P.vk.cplRatio);
      leadsLo += lv * 0.75; leadsHi += lv * 1.25;
      lines.push(['VK Ads', feev, P.vk.setup]);
    }
    if (on('svc_seo')) {
      var fees = round(P.seo.region[val('region')] * P.seo.size[val('seo_size')], 1000);
      monthly += fees; count++;
      lines.push(['SEO', fees, 0]);
    }
    if (on('svc_smm')) {
      var feesm = P.smm.posts[val('smm_posts')] + (on('smm_tg') ? P.smm.telegram : 0) + (on('smm_video') ? P.smm.video : 0);
      monthly += feesm; once += P.smm.setup; count++;
      lines.push(['SMM', feesm, P.smm.setup]);
    }
    var site = P.site[val('site')] || 0;
    if (site) { once += site; lines.push(['Сайт', 0, site]); }
    if (on('analytics')) { once += P.analytics; lines.push(['Сквозная аналитика', 0, P.analytics]); }

    var disc = P.bundle[Math.min(count, 4)] || 0, discSum = round(monthly * disc, 100);
    monthly -= discSum;

    // вывод
    $('[data-r="monthly"]').textContent = rub(monthly);
    $('[data-r="once"]').textContent = rub(once);
    $('[data-r="ads"]').textContent = ads ? rub(ads) : '—';
    var dRow = $('[data-r="disc-row"]');
    dRow.hidden = !discSum;
    $('[data-r="disc"]').textContent = '−' + rub(discSum) + ' (' + Math.round(disc * 100) + '%)';
    var next = P.bundle[Math.min(count + 1, 4)];
    $('[data-r="upsell"]').textContent = count && count < 4 && next > disc
      ? 'Добавьте ещё одну услугу — скидка на ведение вырастет до ' + Math.round(next * 100) + '%.' : '';

    var fc = $('[data-r="forecast"]');
    if (leadsHi > 0) {
      var lo = Math.max(1, Math.round(leadsLo)), hi = Math.max(lo + 1, Math.round(leadsHi));
      var salesLo = lo * P.closeRate, salesHi = hi * P.closeRate;
      var revLo = salesLo * check, revHi = salesHi * check;
      var spend = monthly + ads, midRev = (revLo + revHi) / 2;
      fc.hidden = false;
      $('[data-r="leads"]').textContent = lo + '–' + hi;
      $('[data-r="cpl"]').textContent = rub(round((ads) / ((lo + hi) / 2), 10));
      $('[data-r="sales"]').textContent = Math.max(1, Math.round(salesLo)) + '–' + Math.max(1, Math.round(salesHi));
      $('[data-r="revenue"]').textContent = check ? rub(round(revLo, 1000)) + ' – ' + rub(round(revHi, 1000)) : 'укажите средний чек';
      var romi = check && spend ? Math.round(midRev / spend * 10) / 10 : 0;
      $('[data-r="romi"]').textContent = romi ? '×' + String(romi).replace('.', ',') : '—';
      $('[data-r="romi-note"]').textContent = romi >= 3 ? 'Каждый рубль в маркетинг возвращается ' + String(romi).replace('.', ',') + ' рублями выручки.'
        : romi >= 1 ? 'Окупается. Рост — за счёт конверсии сайта и повторных продаж.'
        : romi ? 'При таком чеке нужен упор на SEO и повторные продажи — обсудим на разборе.' : '';
    } else {
      fc.hidden = true;
    }
    var seoNote = $('[data-r="seo-note"]');
    seoNote.hidden = !(on('svc_seo') || on('svc_smm'));

    // текст расчёта в заявку
    var sum = 'Ниша: ' + niche.name + '; регион: ' + region.name + '; чек: ' + (check ? rub(check) : '—') + '. ' +
      lines.map(function (x) { return x[0] + (x[1] ? ' ' + rub(x[1]) + '/мес' : '') + (x[2] ? ' + разово ' + rub(x[2]) : ''); }).join('; ') +
      '. Итого ' + rub(monthly) + '/мес' + (discSum ? ' (скидка ' + rub(discSum) + ')' : '') + ', разово ' + rub(once) + ', бюджет ' + rub(ads) +
      (leadsHi ? '. Прогноз заявок ' + $('[data-r="leads"]').textContent : '');
    $$('input[name="calc"]').forEach(function (i) { i.value = sum; });
    $('[data-r="empty"]').hidden = count > 0 || site > 0;
    if (fab) fab.textContent = 'Итого ' + rub(monthly) + '/мес → к расчёту';
  }

  // на мобильном плавающая кнопка показывает сумму и ведёт к итогу
  var sumEl = root.querySelector('.calc__sum'), fab = document.querySelector('.float-cta');
  if (fab && sumEl) {
    sumEl.id = 'calc-sum';
    fab.removeAttribute('data-open-lead');
    fab.setAttribute('href', '#calc-sum');
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { fab.style.visibility = e[0].isIntersecting ? 'hidden' : ''; }).observe(sumEl);
    }
  }

  root.addEventListener('input', calc);
  root.addEventListener('change', calc);
  var touched = false;
  root.addEventListener('change', function () {
    if (!touched) { touched = true; try { if (window.ym && window.RG_CONFIG.metrikaId) ym(window.RG_CONFIG.metrikaId, 'reachGoal', 'calc_use'); } catch (e) {} }
  });
  calc();
})();
