#!/usr/bin/env python3
"""Сборка статического сайта «Регион Маркетинг».

Шапка, подвал, форма и контакты заданы здесь один раз — правьте CONFIG
и тексты ниже, затем запустите:  python3 build.py
На выходе — готовые .html в этой же папке, заливаются на любой хостинг.
"""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).parent

# ───────────────────────── КОНТАКТЫ И НАСТРОЙКИ ─────────────────────────
# Всё, что в [квадратных скобках], — заглушки. Заменить перед запуском.
CONFIG = {
    "domain": "https://region-studio.ru",
    "phone": "+7 (000) 000-00-00",            # [заменить]
    "phone_raw": "+70000000000",               # [заменить]
    "email": "hello@region-studio.ru",         # [проверить]
    "telegram": "https://t.me/USERNAME",       # [заменить]
    "whatsapp": "https://wa.me/70000000000",   # [заменить]
    "city": "Москва и Подмосковье, работаем по всей России",
    "legal": "ИП [ФИО], ИНН [000000000000]",   # [заменить]
    "metrika_id": "",                          # номер счётчика Яндекс Метрики
    "year": "2026",
    "slots": "Берём до 5 новых проектов в месяц — каждый веду лично",  # [проверить число]
}

# ───────────────────────── ЦЕНЫ ДЛЯ КАЛЬКУЛЯТОРА ─────────────────────────
# Средние по рынку для малого бизнеса (частные специалисты и небольшие агентства, 2026).
# Меняете цифры здесь → python3 build.py → калькулятор и цены «от» на страницах обновятся.
PRICES = {
    # Яндекс Директ: разовая настройка + ведение в месяц по порогам рекламного бюджета
    "direct": {"setup": 15000, "shopExtra": 7000,
               "fee": [[50000, 15000], [150000, 25000], [300000, 35000], [10**9, 45000]]},
    # VK Ads: то же; cplRatio — во сколько раз заявка из VK дороже/дешевле, чем из Директа
    "vk": {"setup": 12000, "cplRatio": 1.1,
           "fee": [[50000, 15000], [150000, 22000], [10**9, 30000]]},
    # SEO: абонемент по региону × множитель размера сайта
    "seo": {"region": {"local": 25000, "msk": 40000, "rf": 55000},
            "size": {"landing": 0.8, "site": 1, "shop": 1.4}},
    # SMM: по количеству постов в неделю + опции; setup — оформление сообщества
    "smm": {"posts": {"3": 20000, "5": 28000, "7": 36000}, "telegram": 8000, "video": 10000, "setup": 8000},
    "site": {"none": 0, "express": 10000, "landing": 40000, "shop": 80000},
    "analytics": 15000,
    # скидка на ведение за пакет: количество каналов → доля
    "bundle": {"0": 0, "1": 0, "2": 0.05, "3": 0.10, "4": 0.15},
    # доля заявок, которые становятся продажами (для прогноза выручки)
    "closeRate": 0.25,
    # средняя цена заявки из Директа по нишам, ₽ (ориентир для прогноза)
    "niches": {
        "flowers": {"name": "Цветы и подарки", "cpl": 450},
        "food": {"name": "Кафе, доставка еды", "cpl": 350},
        "beauty": {"name": "Красота, медицина", "cpl": 700},
        "repair": {"name": "Ремонт, стройка, услуги для дома", "cpl": 900},
        "auto": {"name": "Авто: продажа и сервис", "cpl": 1200},
        "edu": {"name": "Обучение, курсы", "cpl": 800},
        "realty": {"name": "Недвижимость", "cpl": 2500},
        "b2b": {"name": "B2B, производство, опт", "cpl": 2000},
        "other": {"name": "Другое", "cpl": 1000},
    },
    "regions": {
        "local": {"name": "Мой город / область", "cpl": 1},
        "msk": {"name": "Москва и МО", "cpl": 1.35},
        "rf": {"name": "Вся Россия", "cpl": 1.15},
    },
}


def fmt(n):
    return f"{n:,}".replace(",", " ") + " ₽"


FROM = {  # цены «от» на карточках и страницах услуг — считаются из PRICES
    "sites": fmt(PRICES["site"]["express"]),
    "direct": fmt(PRICES["direct"]["fee"][0][1]) + "/мес",
    "seo": fmt(int(PRICES["seo"]["region"]["local"] * PRICES["seo"]["size"]["landing"])) + "/мес",
    "vk-ads": fmt(PRICES["vk"]["fee"][0][1]) + "/мес",
    "analytics": fmt(PRICES["analytics"]) + " разово",
    "smm": fmt(PRICES["smm"]["posts"]["3"]) + "/мес",
}

SERVICES = [
    # slug, короткое имя (для формы), название в меню, описание карточки, иконка
    ("sites", "Сайт", "Продающие сайты", "Сайты на Tilda под заявки и продажи: лендинги, многостраничники, интернет-магазины. Запуск от 3 дней.", "site"),
    ("direct", "Яндекс Директ", "Яндекс Директ", "Поиск, РСЯ, Мастер кампаний и товарные кампании. Считаем стоимость заявки, а не клики.", "target"),
    ("seo", "SEO", "SEO-продвижение", "Выводим в топ Яндекса и Google по коммерческим запросам. Бесплатный поток заявок на годы.", "search"),
    ("vk-ads", "VK Ads", "Таргет VK Ads", "Реклама во ВКонтакте, Одноклассниках и проектах VK. Лид-формы, сообщения, трафик на сайт.", "megaphone"),
    ("analytics", "Аналитика", "Сквозная аналитика", "Метрика, коллтрекинг, CRM и отчёт: какой канал приносит деньги, а какой только тратит.", "chart"),
    ("smm", "SMM", "SMM", "Ведение сообществ ВК и Telegram: контент-план, посты, оформление. Подписчики, которые покупают.", "chat"),
]

ICONS = {
    "site": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M7 6.5h.01M10 6.5h.01"/><path d="M7 16l3-3 2 2 5-5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/><path d="M7.5 12l2-2 1.5 1.5 2.5-2.5"/>',
    "megaphone": '<path d="M3 10v4a1 1 0 0 0 1 1h3l6 4V5L7 9H4a1 1 0 0 0-1 1z"/><path d="M17 8.5a5 5 0 0 1 0 7M7 15v4"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 21l1.9-5.4A8 8 0 1 1 21 12z"/><path d="M8.5 12h.01M12 12h.01M15.5 12h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "chev": '<path d="m6 9 6 6 6-6"/>',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# ───────────────────────── КЕЙСЫ (цифры — со скриншотов) ─────────────────────────
CASES = {
    "botanika": dict(
        img="botanika", tag="Цветы · интернет-магазин", title="Ботаника — сеть цветочных магазинов",
        money="28 млн ₽", money_cap="доход через сайт за 5 лет",
        stats=[("135 000", "визитов"), ("8 000+", "покупок")],
        text="Интернет-магазин с онлайн-оплатой и доставкой: стабильный поток заказов из поиска и рекламы, в пиковые дни продажи через сайт выше, чем в офлайн-магазинах.",
        alt="Главный экран сайта доставки цветов «Ботаника» в Щёлково"),
    "allo-avto": dict(
        img="allo-avto", tag="Автосалон · Краснодар", title="Алло Авто — автосалон",
        money="35 млн ₽", money_cap="доход за первый месяц после запуска",
        stats=[("12 500", "визитов"), ("26", "продаж авто")],
        text="Запустили сайт под рекламу и поиск — за первый же месяц салон получил поток заявок и закрыл 26 продаж автомобилей.",
        alt="Сайт автосалона «Алло Авто»: баннер «Кредит 4,9% годовых» и спецпредложения"),
    "pyl-da-zhar": dict(
        img="pyl-da-zhar", tag="Кафе и доставка · Щёлково", title="Пыл-да-Жар — кафе и доставка еды",
        money="14 млн ₽", money_cap="доход через сайт за 5 лет",
        stats=[("25 000", "визитов"), ("5 600", "заказов"), ("16%", "конверсия в покупку")],
        text="Сайт с меню, корзиной и онлайн-заказом доставки. Каждый шестой посетитель оформляет заказ — стабильный поток продаж из поиска и рекламы все 5 лет.",
        alt="Сайт кафе «Пыл-да-Жар»: блок «О нас» и меню с шаурмой и шашлыком"),
    "malina": dict(
        img="malina", tag="Цветы · Пушкино", title="Студия цветов MALINA",
        money="20 млн ₽", money_cap="доход через сайт за 3 года",
        stats=[("73 000", "визитов"), ("4 200", "заказов")],
        text="Небольшой цветочный магазин с витриной, корзиной и доставкой онлайн. Сайт приводит заказы каждый день и продаёт далеко за пределы района.",
        alt="Сайт студии цветов MALINA: «Доставка цветов в Пушкино»"),
}

STATS = [("100+", "реализованных проектов"), ("с 2009", "на рынке интернет-маркетинга"),
         ("10–20%", "средняя конверсия наших сайтов"), ("от 3 дней", "до запуска проекта")]


def case_card(key):
    c = CASES[key]
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in c["stats"])
    return f'''<article class="case">
  <div class="case__img"><img src="assets/img/cases/{c["img"]}.webp" alt="{escape(c["alt"])}" loading="lazy" width="650" height="395"></div>
  <div class="case__body">
    <p class="label">{c["tag"]}</p>
    <h3 class="case__title">{c["title"]}</h3>
    <p class="case__money">{c["money"]}</p>
    <p class="case__money-cap">{c["money_cap"]}</p>
    <div class="case__stats">{stats}</div>
    <p class="case__text">{c["text"]}</p>
  </div>
</article>'''


# ───────────────────────── ОБЩИЕ БЛОКИ ─────────────────────────

def header(active):
    def cur(p):
        return ' aria-current="page"' if active == p else ""
    svc_links = "".join(
        f'<a href="{s}.html"{cur(s)}>{menu}</a>'
        for s, _, menu, _, _ in SERVICES)
    mob = "".join(f'<a href="{s}.html">{menu}</a>' for s, _, menu, _, _ in SERVICES)
    return f'''<a class="skip" href="#main">К содержанию</a>
<header class="header">
  <div class="container header__in">
    <a class="header__logo" href="index.html" aria-label="Регион Маркетинг — на главную"><img src="assets/img/logo-light.svg" alt="Регион Маркетинг" width="150" height="48"></a>
    <nav class="nav" aria-label="Основное меню">
      <div class="nav__drop"><button type="button" aria-expanded="false" aria-haspopup="true">Услуги {icon("chev", "icon")}</button><div class="nav__menu">{svc_links}</div></div>
      <a href="calculator.html"{cur("calculator")}>Цены</a>
      <a href="cases.html"{cur("cases")}>Кейсы</a>
      <a href="index.html#process">Как работаем</a>
      <a href="contacts.html"{cur("contacts")}>Контакты</a>
    </nav>
    <a class="header__phone" href="tel:{CONFIG["phone_raw"]}">{CONFIG["phone"]}</a>
    <a class="rg-btn rg-btn--primary header__cta" href="#lead" data-open-lead>Получить расчёт</a>
    <button class="burger" type="button" aria-label="Меню" aria-expanded="false">{icon("menu")}</button>
  </div>
</header>
<nav class="mobile-nav" aria-label="Мобильное меню">
  {mob}
  <a href="calculator.html">Калькулятор цены</a>
  <a href="cases.html">Кейсы</a>
  <a href="contacts.html">Контакты</a>
  <a href="tel:{CONFIG["phone_raw"]}">{CONFIG["phone"]}</a>
  <a class="rg-btn rg-btn--primary" href="#lead" data-open-lead>Получить расчёт</a>
</nav>'''


def footer():
    svc = "".join(f'<li><a href="{s}.html">{menu}</a></li>' for s, _, menu, _, _ in SERVICES)
    return f'''<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="stack">
        <img class="footer__logo" src="assets/img/logo-dark.svg" alt="Регион Маркетинг" width="170" height="55" loading="lazy">
        <p class="muted" style="color:var(--ink-inverse-muted);max-width:300px">Делаем продающие сайты и обеспечиваем поток клиентов. С 2009 года.</p>
      </div>
      <div><h4>Услуги</h4><ul>{svc}</ul></div>
      <div><h4>Агентство</h4><ul><li><a href="calculator.html">Калькулятор цены</a></li><li><a href="cases.html">Кейсы</a></li><li><a href="index.html#process">Как работаем</a></li><li><a href="index.html#faq">Вопросы</a></li><li><a href="contacts.html">Контакты</a></li></ul></div>
      <div><h4>Связаться</h4><ul>
        <li><a href="tel:{CONFIG["phone_raw"]}">{CONFIG["phone"]}</a></li>
        <li><a href="mailto:{CONFIG["email"]}">{CONFIG["email"]}</a></li>
        <li><a href="{CONFIG["telegram"]}" target="_blank" rel="noopener">Telegram</a> · <a href="{CONFIG["whatsapp"]}" target="_blank" rel="noopener">WhatsApp</a></li>
        <li style="color:var(--ink-inverse-muted)">{CONFIG["city"]}</li>
      </ul></div>
    </div>
    <div class="footer__bottom">
      <span>© 2009–{CONFIG["year"]} Регион Маркетинг · {CONFIG["legal"]}</span>
      <a href="privacy.html">Политика обработки персональных данных</a>
    </div>
  </div>
</footer>
<a class="rg-btn rg-btn--primary float-cta" href="#lead" data-open-lead>Получить расчёт</a>'''


def form_fields(prefix, preselect=None):
    chips = "".join(
        f'<label><input type="checkbox" name="service[]" value="{short}"{" checked" if slug == preselect else ""}><span>{short}</span></label>'
        for slug, short, _, _, _ in SERVICES)
    return f'''<fieldset class="chips"><legend>Что нужно</legend>{chips}</fieldset>
    <div class="row2">
      <div class="field"><label for="{prefix}-name">Имя</label><input id="{prefix}-name" name="name" autocomplete="name" placeholder="Как к вам обращаться"></div>
      <div class="field"><label for="{prefix}-phone">Телефон *</label><input id="{prefix}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required></div>
    </div>
    <div class="field"><label for="{prefix}-site">Сайт или ниша</label><input id="{prefix}-site" name="site" placeholder="Например: доставка цветов, Щёлково"></div>
    <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="consent"><input type="checkbox" name="consent" required><span>Согласен на обработку персональных данных по <a href="privacy.html" target="_blank">политике</a></span></label>
    <button class="rg-btn rg-btn--on-accent" type="submit">Получить расчёт</button>
    <p class="form-note" role="status" aria-live="polite"></p>'''


def cta_section(preselect=None, title='Посчитаем, сколько <em>заявок</em> даст ваш бюджет',
                text="Оставьте телефон — за 1 рабочий день разберём нишу и конкурентов и пришлём расчёт: сколько стоит заявка и сколько их будет. Бесплатно и без обязательств."):
    return f'''<section class="section section--accent" id="lead">
  <div class="container cta__grid">
    <div>
      <p class="label">Бесплатный расчёт</p>
      <h2 class="rg-headline h1" style="margin-top:16px">{title}</h2>
      <p class="lead">{text}</p>
      <ul class="checks" style="margin-top:32px">
        <li>Прогноз заявок и цены лида по вашей нише</li>
        <li>Разбор 3 конкурентов: где они берут клиентов</li>
        <li>План запуска с цифрами — останется у вас</li>
      </ul>
      <div class="cta__contacts">
        <span>Или напишите напрямую:</span>
        <a href="tel:{CONFIG["phone_raw"]}">{CONFIG["phone"]}</a>
        <a href="{CONFIG["telegram"]}" target="_blank" rel="noopener">Telegram →</a>
      </div>
    </div>
    <form class="lead-form" novalidate>
    {form_fields("cta", preselect)}
    </form>
  </div>
</section>'''


def modal():
    return f'''<dialog class="modal" id="lead-modal" aria-labelledby="modal-title">
  <div class="modal__in">
    <button class="modal__close" type="button" aria-label="Закрыть">{icon("close")}</button>
    <h2 class="h3" id="modal-title">Бесплатный разбор вашего маркетинга</h2>
    <p class="muted">Перезвоним в течение рабочего часа. За 1 день пришлём прогноз заявок, цену лида и план запуска — даже если не будем работать вместе.</p>
    <form class="lead-form" novalidate>
    {form_fields("m")}
    </form>
  </div>
</dialog>'''


def page(slug, title, description, body, active=None, noindex=False, with_cta=True, preselect=None, cta_kwargs=None, with_calc=False):
    metrika = ""
    if CONFIG["metrika_id"]:
        mid = CONFIG["metrika_id"]
        metrika = f'''<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return;}}}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({mid},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script><noscript><div><img src="https://mc.yandex.ru/watch/{mid}" style="position:absolute;left:-9999px" alt=""></div></noscript>'''
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    url = CONFIG["domain"] + ("/" if slug == "index" else f"/{slug}.html")
    cfg_js = (f'window.RG_CONFIG={{metrikaId:{CONFIG["metrika_id"] or "null"},formEndpoint:"send.php",thanksPage:"thanks.html",'
              f'phone:"{CONFIG["phone"]}",phoneRaw:"{CONFIG["phone_raw"]}",telegram:"{CONFIG["telegram"]}"}};')
    calc_js = (f'<script>window.RG_PRICES={json.dumps(PRICES, ensure_ascii=False)};</script>'
               '<script src="assets/js/calc.js" defer></script>') if with_calc else ""
    cta = cta_section(preselect, **(cta_kwargs or {})) if with_cta else ""
    html = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ru_RU">
<meta name="theme-color" content="#6147ff">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/Gilroy-Regular.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/Gilroy-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
{metrika}
</head>
<body>
{header(active or slug)}
<main id="main">
{body}
{cta}
</main>
{footer()}
{modal()}
<script>{cfg_js}</script>
<script src="assets/js/main.js" defer></script>
{calc_js}
</body>
</html>
'''
    (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")


# ───────────────────────── КАЛЬКУЛЯТОР ─────────────────────────

def _radios(name, options, checked):
    return "".join(
        f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == checked else ""}><span>{t}</span></label>'
        for v, t in options)


def _range(name, lo, hi, step, value, label):
    return f'''<div class="calc-range">
        <div class="calc-range__top"><label for="c-{name}">{label}</label><output data-out="{name}">{fmt(value)}</output></div>
        <input id="c-{name}" type="range" name="{name}" min="{lo}" max="{hi}" step="{step}" value="{value}">
        <div class="calc-range__scale"><span>{fmt(lo)}</span><span>{fmt(hi)}</span></div>
      </div>'''


def _svc(key, title, sub, opts, checked=True):
    return f'''<div class="calc-svc" data-svc="{key}">
      <label class="calc-svc__head">
        <input type="checkbox" name="svc_{key.split("-")[0]}"{" checked" if checked else ""}>
        <span class="calc-svc__check" aria-hidden="true"></span>
        <span><b>{title}</b><small>{sub}</small></span>
      </label>
      <div class="calc-svc__opts">{opts}</div>
    </div>'''


def calculator(heading=True):
    niches = "".join(f'<option value="{k}"{" selected" if k == "flowers" else ""}>{v["name"]}</option>' for k, v in PRICES["niches"].items())
    regions = _radios("region", [(k, v["name"]) for k, v in PRICES["regions"].items()], "local")
    head = '''<div class="section__head">
      <div><p class="label">Калькулятор</p><h2 class="rg-headline h2" style="margin-top:12px">Сколько стоит маркетинг и сколько <em>заявок</em> он принесёт</h2></div>
      <p class="muted">Выберите каналы — калькулятор посчитает цену и прогноз заявок по средним данным вашей ниши. Цена из калькулятора фиксируется в договоре.</p>
    </div>''' if heading else ""
    return f'''<section class="section section--raised" id="calculator">
  <div class="container">
    {head}
    <div class="calc" id="calc">
      <div class="calc__form">
        <fieldset class="calc-step">
          <legend><span>1</span> Ваш бизнес</legend>
          <div class="row2">
            <div class="field"><label for="c-niche">Ниша</label><select id="c-niche" name="niche">{niches}</select></div>
            <div class="field"><label for="c-check">Средний чек, ₽</label><input id="c-check" name="check" type="number" min="0" step="500" value="5000" inputmode="numeric"></div>
          </div>
          <div class="field"><span class="field__label">Где ваши клиенты</span><div class="opts">{regions}</div></div>
        </fieldset>

        <fieldset class="calc-step">
          <legend><span>2</span> Каналы привлечения</legend>
          {_svc("direct", "Яндекс Директ", "Поиск, РСЯ — заявки с первой недели",
                _range("direct_budget", 20000, 500000, 5000, 60000, "Рекламный бюджет в месяц") +
                '<label class="tick"><input type="checkbox" name="direct_shop"><span>Товарные кампании / Мастер кампаний (для магазинов)</span></label>')}
          {_svc("vk-ads", "Таргет VK Ads", "ВКонтакте, Одноклассники, лид-формы",
                _range("vk_budget", 15000, 300000, 5000, 30000, "Рекламный бюджет в месяц"), checked=False)}
          {_svc("seo", "SEO-продвижение", "Топ Яндекса и Google — заявки без оплаты за клик",
                '<div class="field"><span class="field__label">Сайт</span><div class="opts">' + _radios("seo_size", [("landing", "Лендинг"), ("site", "Сайт до 50 стр."), ("shop", "Интернет-магазин")], "site") + '</div></div>', checked=False)}
          {_svc("smm", "SMM", "Ведение сообществ ВК и Telegram",
                '<div class="field"><span class="field__label">Постов в неделю</span><div class="opts">' + _radios("smm_posts", [("3", "3"), ("5", "5"), ("7", "7")], "3") + '</div></div>'
                '<label class="tick"><input type="checkbox" name="smm_tg"><span>+ Telegram-канал</span></label>'
                '<label class="tick"><input type="checkbox" name="smm_video"><span>+ Клипы и истории</span></label>', checked=False)}
        </fieldset>

        <fieldset class="calc-step">
          <legend><span>3</span> Дополнительно</legend>
          <div class="field"><span class="field__label">Сайт</span><div class="opts">{_radios("site", [("none", "Уже есть"), ("express", "Экспресс-сайт · " + fmt(PRICES["site"]["express"])), ("landing", "Продающий лендинг · " + fmt(PRICES["site"]["landing"])), ("shop", "Магазин / многостраничник · " + fmt(PRICES["site"]["shop"]))], "none")}</div></div>
          <label class="tick"><input type="checkbox" name="analytics"><span>Сквозная аналитика: коллтрекинг + CRM · {fmt(PRICES["analytics"])} разово</span></label>
        </fieldset>
      </div>

      <aside class="calc__sum" aria-live="polite">
        <p class="calc__sum-label">Ведение в месяц</p>
        <p class="calc__big" data-r="monthly">0 ₽</p>
        <dl class="calc__rows">
          <div data-r="disc-row" hidden><dt>Скидка за пакет</dt><dd data-r="disc"></dd></div>
          <div><dt>Разово: настройка, сайт</dt><dd data-r="once">0 ₽</dd></div>
          <div><dt>Рекламный бюджет<br><small>платите напрямую в Яндекс / VK</small></dt><dd data-r="ads">—</dd></div>
        </dl>
        <p class="calc__upsell" data-r="upsell"></p>
        <p class="calc__empty" data-r="empty" hidden>Выберите хотя бы один канал.</p>

        <div class="calc__fc" data-r="forecast">
          <p class="calc__sum-label">Прогноз на месяц</p>
          <div class="calc__fc-grid">
            <div><b data-r="leads">—</b><span>заявок</span></div>
            <div><b data-r="cpl">—</b><span>цена заявки</span></div>
            <div><b data-r="sales">—</b><span>продаж</span></div>
            <div><b data-r="romi">—</b><span>окупаемость</span></div>
          </div>
          <p class="calc__rev">Выручка: <b data-r="revenue">—</b></p>
          <p class="calc__note" data-r="romi-note"></p>
        </div>
        <p class="calc__note" data-r="seo-note" hidden>SEO и SMM работают накопительно: первые заявки из поиска — через 2–4 месяца, дальше поток растёт без оплаты за клик.</p>

        <form class="lead-form calc__form-lead" novalidate>
          <input type="hidden" name="calc" value="">
          <input type="hidden" name="service[]" value="Калькулятор">
          <div class="field"><label for="calc-phone">Телефон — пришлём точный расчёт</label><input id="calc-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required></div>
          <input class="hp" type="text" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
          <label class="consent"><input type="checkbox" name="consent" required><span>Согласен с <a href="privacy.html" target="_blank">политикой обработки данных</a></span></label>
          <button class="rg-btn rg-btn--primary" type="submit">Зафиксировать цену</button>
          <p class="form-note" role="status" aria-live="polite"></p>
        </form>
        <p class="calc__fine">Прогноз — по средней цене заявки в нише за 2025–2026 гг. Точные цифры по вашему региону и конкурентам — после бесплатного разбора.</p>
      </aside>
    </div>
  </div>
</section>'''


# ───────────────────────── ГЛАВНАЯ ─────────────────────────

HERO_ART = '''<div class="hero__art" aria-hidden="true">
  <svg viewBox="0 0 480 480" preserveAspectRatio="xMidYMid slice">
    <rect x="96" y="0" width="64" height="48" fill="#787878"/>
    <rect x="48" y="48" width="208" height="432" fill="#1d1d1e"/>
    <rect x="160" y="0" width="320" height="480" fill="#6147ff"/>
    <polyline class="growth" stroke="#f3f3f3" points="0,400 72,340 112,412 160,372 208,428 312,168 360,252 400,140 492,40"/>
  </svg>
  <div class="hero__badge"><b>+26 продаж</b><span>автосалону за первый месяц</span></div>
</div>'''

PAINS = [
    ("Отдали 50 000 ₽ на рекламу — пришли три заявки, и те нецелевые", "Кампании собраны «на всё подряд», минус-слов нет, РСЯ крутится на мобильных играх."),
    ("Подрядчик присылает отчёт с кликами и показами", "Сколько заявок и продаж — не знает никто. Непонятно, за что вы платите каждый месяц."),
    ("Сайт есть, но клиенты — только по сарафану", "Сайт красивый, но не отвечает на вопросы клиента и не ведёт к звонку."),
    ("Конкурент в топе Яндекса, а вас там нет", "Клиенты ищут «доставка цветов рядом» и находят не вас. Каждый день."),
]

GUARANTEES = [
    ("Цена — в договоре", "Стоимость из расчёта фиксируем до старта. Не растёт в процессе."),
    ("Всё — ваше", "Сайт, домен, рекламные кабинеты и Метрика оформлены на вас с первого дня."),
    ("Без договора на год", "Помесячная оплата. Остаёмся, потому что приносим заявки, а не из-за штрафов."),
    ("Отчёт в рублях", "Каждую неделю: сколько заявок, по какой цене, из какого канала."),
]


def build_index():
    services = ""
    for slug, short, menu, desc, ic in SERVICES:
        feat = " service--featured" if slug == "direct" else ""
        services += f'''<a class="card service{feat}" href="{slug}.html">
      <span class="service__icon">{icon(ic)}</span>
      <h3 class="h3">{menu}</h3>
      <p>{desc}</p>
      <p class="service__price">от {FROM[slug]}</p>
      <span class="service__more">Подробнее {icon("arrow")}</span>
    </a>'''
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in STATS)
    cases = "".join(case_card(k) for k in ["botanika", "allo-avto", "pyl-da-zhar", "malina"])
    pains = "".join(f'<div class="card pain"><h3 class="h3">«{t}»</h3><p class="muted">{x}</p></div>' for t, x in PAINS)
    guar = "".join(f'<div class="guar"><h3 class="h3">{t}</h3><p class="muted">{x}</p></div>' for t, x in GUARANTEES)
    body = f'''<section class="hero">
  <div class="container hero__grid">
    <div>
      <p class="label">Маркетинг для малого бизнеса под ключ</p>
      <h1 class="rg-headline display">Заявки для вашего бизнеса — <em>уже через неделю</em></h1>
      <p class="lead">Сайт, Яндекс Директ, VK Ads, SEO и SMM одной командой. Строим маркетинг так, чтобы он стоил не больше 10% от выручки, — и показываем расчёт до старта.</p>
      <ul class="checks hero__checks">
        <li>Первые заявки из Директа — в первую неделю</li>
        <li>Отчёт в заявках и рублях, а не в кликах</li>
        <li>Цена фиксируется в договоре</li>
      </ul>
      <div class="btn-row">
        <a class="rg-btn rg-btn--primary rg-btn--lg" href="#calculator">Рассчитать стоимость</a>
        <a class="rg-btn rg-btn--secondary rg-btn--lg" href="#lead" data-open-lead>Бесплатный разбор</a>
      </div>
      <p class="hero__slots"><img src="assets/img/founder-avatar.webp" alt="" width="40" height="40">{CONFIG["slots"]}</p>
    </div>
    {HERO_ART}
  </div>
  <div class="container">
    <div class="proof">
      <div><b>97 млн ₽</b><span>заработали клиенты через наши сайты</span></div>
      <div><b>100+</b><span>проектов с 2009 года</span></div>
      <div><b>10–20%</b><span>средняя конверсия сайтов</span></div>
      <div><b>0%</b><span>рассрочка на услуги через Т-Банк</span></div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Узнаёте <em>свой бизнес</em>?</h2>
      <p class="muted">С этим к нам приходит большинство владельцев бизнеса. Каждый месяц в такой ситуации — это деньги, которые уходят конкурентам.</p>
    </div>
    <div class="grid grid--4 pains">{pains}</div>
    <p class="pains__answer">Мы собираем <b>сайт, рекламу и аналитику в одну связку</b> и отвечаем за результат целиком: сколько заявок, по какой цене, сколько продаж.</p>
  </div>
</section>

<section class="section" id="services">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Шесть инструментов, <em>одна цель</em> — заявки</h2>
      <p class="muted">Берём проект целиком или отдельный канал. Цены — средние по рынку, без «от 5 000 ₽, а потом допродажи».</p>
    </div>
    <div class="grid grid--3">{services}</div>
  </div>
</section>

<section class="section section--raised" id="cases">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Не обещаем — <em>показываем</em> деньги клиентов</h2>
      <a class="rg-btn rg-btn--secondary" href="cases.html">Все кейсы</a>
    </div>
    <div class="cases">{cases}</div>
  </div>
</section>

{calculator().replace("section section--raised", "section")}

<section class="section section--ink">
  <div class="container">
    <div class="section__head"><h2 class="rg-headline h2">Работаем на результат <em>с 2009 года</em></h2></div>
    <div class="stats">{stats}</div>
  </div>
</section>

<section class="section" id="process">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">От звонка до первых заявок — <em>7 дней</em></h2>
      <p class="muted">Вы видите план, сроки и цифры до того, как заплатите.</p>
    </div>
    <ol class="steps">
      <li><h3 class="h3">Разбор · день 1</h3><p>Созвон 30 минут: ниша, средний чек, маржа, текущие каналы. Считаем, какая цена заявки окупается.</p></li>
      <li><h3 class="h3">Расчёт · день 2</h3><p>Прогноз заявок, бюджет и план запуска. Фиксируем цену и сроки в договоре.</p></li>
      <li><h3 class="h3">Запуск · дни 3–7</h3><p>Сайт, кампании, Метрика и цели. Первые заявки — уже в первую неделю.</p></li>
      <li><h3 class="h3">Рост · каждый месяц</h3><p>Чистим трафик, тестируем гипотезы, снижаем цену заявки. Отчёт — в рублях.</p></li>
    </ol>
  </div>
</section>

<section class="section section--raised">
  <div class="container">
    <div class="section__head"><h2 class="rg-headline h2">Рискуете <em>только временем</em> на созвон</h2></div>
    <div class="grid grid--4">{guar}</div>
  </div>
</section>

<section class="section">
  <div class="container founder">
    <div class="founder__media">
      <div class="founder__img"><img src="assets/img/founder.webp" alt="Александр Нестеров, основатель агентства «Регион Маркетинг»" width="800" height="1202" loading="lazy"></div>
      <div class="founder__badge"><b>25 лет</b><span>в маркетинге</span></div>
    </div>
    <div>
      <p class="label">Кто отвечает за результат</p>
      <h2 class="rg-headline h2" style="margin:12px 0 24px">Александр Нестеров, <em>основатель</em></h2>
      <p class="lead">25 лет в маркетинге. Руководил маркетинговыми направлениями в LG Electronics, Sony и Indesit, с 2009 года — в интернет-маркетинге для малого и среднего бизнеса.</p>
      <blockquote class="founder__quote">«Я лично веду каждый проект. Вы общаетесь не с менеджером, который пересказывает задачу, а с тем, кто настраивает рекламу и отвечает за цифры».</blockquote>
      <div class="btn-row"><a class="rg-btn rg-btn--primary" href="#lead" data-open-lead>Обсудить проект</a><a class="rg-btn rg-btn--secondary" href="{CONFIG["telegram"]}" target="_blank" rel="noopener">Написать в Telegram</a></div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="container express">
    <div>
      <p class="label">Нет сайта? Начните с малого</p>
      <h2 class="rg-headline h1" style="margin:12px 0 16px">Экспресс-сайт за <em>{fmt(PRICES["site"]["express"])}</em> и 3 дня</h2>
      <p class="lead muted">Готовый продающий шаблон под вашу нишу: оффер, каталог, форма заявки, Метрика. Без правок — поэтому быстро и недорого. Можно в рассрочку: от 460 ₽ в месяц.</p>
    </div>
    <div class="express__cta">
      <ul class="checks"><li>Запуск за 3 дня</li><li>Готов к рекламе в Директе и VK</li><li>Сайт и домен — ваши</li></ul>
      <a class="rg-btn rg-btn--on-accent rg-btn--lg" href="#lead" data-open-lead data-service="Сайт">Хочу экспресс-сайт</a>
    </div>
  </div>
</section>

<section class="section" id="faq">
  <div class="container split">
    <h2 class="rg-headline h2">Частые <em>вопросы</em></h2>
    <div class="faq">
      <details><summary>Сколько стоит?</summary><p>Ведение Директа — от {FROM["direct"]}, VK Ads — от {FROM["vk-ads"]}, SEO — от {FROM["seo"]}, SMM — от {FROM["smm"]}, сайт — от {FROM["sites"]}. Точную сумму для вашей ниши покажет <a href="#calculator">калькулятор</a>, а на разборе зафиксируем её в договоре.</p></details>
      <details><summary>Когда будут первые заявки?</summary><p>Из Яндекс Директа и VK Ads — обычно в первую неделю после запуска. SEO — накопительный канал: первые позиции через 2–4 месяца, дальше поток растёт без оплаты за клик.</p></details>
      <details><summary>А если заявок не будет?</summary><p>До старта считаем прогноз и показываем, на какую цену заявки ориентируемся. Если через месяц цифры хуже прогноза — разбираем причины и перестраиваем кампании без доплат. Договор помесячный: держать вас нечем, кроме результата.</p></details>
      <details><summary>Рекламный бюджет платится вам?</summary><p>Нет. Бюджет вы пополняете сами в своём кабинете Яндекса или VK — деньги под вашим контролем. Нам платите только за работу.</p></details>
      <details><summary>Можно в рассрочку?</summary><p>Да, через Т-Банк — без переплаты.</p></details>
      <details><summary>Вы работаете с регионами?</summary><p>Да. Большая часть клиентов — локальный бизнес Подмосковья и регионов: Щёлково, Пушкино, Краснодар. Работаем удалённо по всей России.</p></details>
    </div>
  </div>
</section>'''
    page("index", "Регион Маркетинг — заявки для малого бизнеса: сайты, Яндекс Директ, SEO, VK Ads, SMM",
         "Маркетинг для малого бизнеса под ключ: сайт, Яндекс Директ, VK Ads, SEO и SMM. Калькулятор стоимости и прогноз заявок. 97 млн ₽ дохода клиентов, 100+ проектов с 2009 года.",
         body, with_calc=True,
         cta_kwargs=dict(title="Узнайте, сколько <em>заявок</em> недополучаете",
                         text="Бесплатный разбор за 1 день: прогноз заявок и цены лида для вашей ниши, 3 конкурента и где они берут клиентов, план запуска с цифрами. Останется у вас, даже если не будем работать вместе."))


def build_calculator():
    body = f'''<section class="page-hero" style="padding-bottom:32px">
  <div class="container">
    <p class="crumbs"><a href="index.html">Главная</a> / Калькулятор</p>
    <h1 class="rg-headline h1">Калькулятор <em>стоимости</em> маркетинга</h1>
    <p class="lead">Яндекс Директ, VK Ads, SEO и SMM — цена ведения, разовые работы и прогноз заявок для вашей ниши за минуту. Цена из калькулятора фиксируется в договоре.</p>
  </div>
</section>
{calculator(heading=False)}'''
    page("calculator", "Калькулятор стоимости: Яндекс Директ, VK Ads, SEO, SMM — Регион Маркетинг",
         "Посчитайте стоимость Яндекс Директа, VK Ads, SEO и SMM для своего бизнеса и прогноз заявок по нише. Скидка до 15% на пакет услуг.",
         body, with_calc=True)


# ───────────────────────── СТРАНИЦЫ УСЛУГ ─────────────────────────

SERVICE_PAGES = {
    "sites": dict(
        title="Продающие сайты на Tilda под ключ — Регион Маркетинг",
        desc="Разработка продающих сайтов на Tilda: лендинги, многостраничные сайты, интернет-магазины. Средняя конверсия 10–20%, запуск от 3 дней.",
        h1="Сайты, которые <em>продают</em>, а не просто красиво выглядят",
        lead="Лендинги, многостраничные сайты и интернет-магазины на Tilda. Структура под рекламу и поиск, онлайн-оплата, корзина, интеграция с CRM. Запуск от 3 дней.",
        kpi=[("10–20%", "средняя конверсия наших сайтов"), ("от 3 дней", "до запуска"), ("97 млн ₽", "дохода клиентов через 4 сайта из кейсов")],
        for_whom=["Нужен сайт под рекламу, а текущий не конвертирует", "Продаёте офлайн и хотите принимать заказы онлайн", "Сайт есть, но заявок из него нет — нужна пересборка", "Запускаете новое направление и нужен быстрый тест спроса"],
        includes=[("Прототип под заявки", "Структура по вопросам клиента: оффер, выгоды, доверие, цена, призыв. Сначала смысл — потом дизайн."),
                  ("Тексты", "Пишем продающие тексты сами. Без воды и «индивидуального подхода»."),
                  ("Дизайн на Tilda", "Адаптив под телефоны: 70–80% трафика — мобильный."),
                  ("Корзина и оплата", "Каталог, корзина, онлайн-оплата, доставка — для интернет-магазинов."),
                  ("Аналитика", "Метрика, цели на заявки и звонки, передача заявок в Telegram или CRM."),
                  ("Базовое SEO", "Мета-теги, структура, скорость, sitemap — сайт готов к продвижению.")],
        cases=["botanika", "malina"],
        faq=[("Почему Tilda, а не WordPress?", "Tilda быстрее в запуске и дешевле в поддержке: правки делаются без программиста, хостинг и безопасность уже включены. Для 90% задач малого бизнеса этого достаточно."),
             ("Сайт будет моим?", "Да. Аккаунт Tilda и домен оформляются на вас."),
             ("Можно переделать существующий сайт?", "Да. Начинаем с аудита: где теряются заявки. Иногда хватает пересборки первого экрана и формы.")]),
    "direct": dict(
        title="Настройка и ведение Яндекс Директ — Регион Маркетинг",
        desc="Настройка и ведение Яндекс Директ под заявки: поиск, РСЯ, Мастер кампаний, товарные кампании. Считаем стоимость заявки и продажи. Первые заявки в первую неделю.",
        h1="Заявки из <em>Яндекс Директа</em> по понятной цене",
        lead="Настраиваем и ведём поиск, РСЯ, Мастер кампаний и товарные кампании. Работаем в Direct Commander, чистим минус-слова и площадки еженедельно. Отчёт — в заявках и рублях.",
        kpi=[("1 неделя", "до первых заявок"), ("еженедельно", "чистка площадок и минус-слов"), ("35 млн ₽", "доход Алло Авто за первый месяц")],
        for_whom=["Реклама крутится, а заявки дорогие или нецелевые", "Нужен быстрый поток клиентов, SEO ждать некогда", "Предыдущий подрядчик отчитывался кликами", "Запускаете новый сайт и нужен трафик с первого дня"],
        includes=[("Аудит и семантика", "Собираем ключи по спросу, отсекаем информационные и мусорные запросы."),
                  ("Поиск и РСЯ", "Отдельные кампании под горячий спрос и под охват, свои объявления под каждую группу."),
                  ("Мастер кампаний и товарка", "Для интернет-магазинов — товарные кампании по фиду."),
                  ("Ретаргетинг", "Догоняем тех, кто был на сайте и не оставил заявку."),
                  ("Цели и конверсии", "Стратегии на оплату за конверсии, когда статистики достаточно."),
                  ("Еженедельное ведение", "Ставки, минус-слова, площадки РСЯ, тесты объявлений.")],
        cases=["allo-avto", "botanika"],
        faq=[("Какой нужен рекламный бюджет?", "Зависит от ниши и региона. Считаем прогноз по статистике Вордстата и конкурентам — присылаем вместе с расчётом."),
             ("Бюджет оплачивается вам?", "Нет. Рекламный бюджет вы пополняете сами в своём кабинете — деньги под вашим контролем."),
             ("Что если заявки дорогие?", "Разбираем по цепочке: запросы → объявления → сайт → обработка заявок. Часто проблема в посадочной странице, её тоже чиним.")]),
    "seo": dict(
        title="SEO-продвижение сайтов в Яндекс и Google — Регион Маркетинг",
        desc="SEO-продвижение в Яндексе и Google по коммерческим запросам для локального бизнеса. Техническая оптимизация, контент, ссылки. Заявки без оплаты за клик.",
        h1="Клиенты из поиска <em>без оплаты за клик</em>",
        lead="Выводим сайт в топ Яндекса и Google по коммерческим запросам вашего города. SEO — накопительный канал: заявки идут годами, а стоимость лида со временем падает.",
        kpi=[("135 000", "визитов на сайт Ботаники"), ("73 000", "визитов на сайт MALINA"), ("2–4 мес.", "до первых позиций")],
        for_whom=["Реклама съедает маржу и хочется бесплатный канал", "Конкуренты в топе, а вас в поиске нет", "Локальный бизнес: «доставка цветов в Щёлково» — ваш запрос", "Сайт есть, но трафик падает"],
        includes=[("Технический аудит", "Скорость, индексация, дубли, мобильная версия, ошибки в коде."),
                  ("Семантика и структура", "Под каждый кластер запросов — своя страница."),
                  ("Тексты и мета-теги", "Контент под запросы и под людей: чтобы и ранжировался, и продавал."),
                  ("Локальное SEO", "Яндекс Бизнес и Google Maps: карточка, отзывы, фото."),
                  ("Ссылки и упоминания", "Каталоги, отраслевые площадки, крауд — без спама."),
                  ("Отчёт по позициям", "Ежемесячно: позиции, трафик, заявки из поиска.")],
        cases=["botanika", "malina"],
        faq=[("Даёте гарантии топа?", "Гарантировать позиции честно никто не может — алгоритмы у Яндекса. Мы фиксируем план работ и показываем динамику трафика и заявок каждый месяц."),
             ("Можно продвигать сайт на Tilda?", "Да. Два наших кейса из топа — на Tilda."),
             ("Сколько длится продвижение?", "Первые результаты — через 2–4 месяца. Дальше — поддержка и расширение семантики.")]),
    "vk-ads": dict(
        title="Таргетированная реклама VK Ads — Регион Маркетинг",
        desc="Настройка таргетированной рекламы VK Ads: ВКонтакте, Одноклассники, проекты VK. Лид-формы, сообщения в сообщество, трафик на сайт.",
        h1="Таргет <em>VK Ads</em>: клиенты из соцсетей",
        lead="Настраиваем рекламу во ВКонтакте, Одноклассниках и проектах VK. Лид-формы, сообщения в сообщество, трафик на сайт — выбираем формат под нишу и средний чек.",
        kpi=[("3 формата", "лид-формы, сообщения, сайт"), ("A/B", "тесты креативов с первой недели"), ("от 2 дней", "до запуска")],
        for_whom=["Товар, который покупают глазами: цветы, еда, товары для дома", "Директ перегрет, нужен второй канал", "Есть сообщество ВК и хочется из него продаж", "Нужно продвигать акцию или открытие точки"],
        includes=[("Аудитории", "Интересы, ключевые фразы, гео, look-alike, ретаргетинг по базе."),
                  ("Креативы", "Тексты и баннеры под аудитории, тесты гипотез."),
                  ("Лид-формы", "Заявка без перехода на сайт — ниже цена лида."),
                  ("Пиксель и цели", "Пиксель VK на сайт, конверсии, оптимизация на заявки."),
                  ("Ведение", "Отключаем слабые объявления, масштабируем сильные."),
                  ("Отчёт", "Заявки, цена лида, продажи — раз в неделю.")],
        cases=["pyl-da-zhar", "malina"],
        faq=[("VK Ads подходит для B2B?", "Хуже, чем Директ, но работает для узких ниш с чётким портретом клиента. Проверяем тестом на небольшом бюджете."),
             ("Нужно ли сообщество?", "Не обязательно — можно вести на сайт или в лид-форму. Но живое сообщество повышает доверие.")]),
    "analytics": dict(
        title="Сквозная аналитика для бизнеса — Регион Маркетинг",
        desc="Настройка сквозной аналитики: Яндекс Метрика, цели, коллтрекинг, интеграция с CRM. Видно, какой канал приносит деньги.",
        h1="Сквозная аналитика: видно, <em>где деньги</em>",
        lead="Связываем рекламу, сайт, звонки и CRM в одну картину. Видно, какой канал приносит продажи, а какой только тратит бюджет.",
        kpi=[("100%", "заявок с источником"), ("звонки", "учитываются через коллтрекинг"), ("1 отчёт", "вместо пяти кабинетов")],
        for_whom=["Реклама идёт в несколько каналов, а откуда продажи — непонятно", "Много звонков, а источник не записывается", "Руководитель хочет видеть деньги, а не клики", "Нужно сокращать бюджет и страшно отключить не то"],
        includes=[("Метрика и цели", "Заявки, звонки, клики в мессенджеры, оплаты — всё размечено."),
                  ("UTM-разметка", "Единые правила меток для всех каналов."),
                  ("Коллтрекинг", "Подменные номера — видно, какая реклама дала звонок."),
                  ("CRM", "Передача заявок с источником в amoCRM, Битрикс24 или Telegram."),
                  ("Офлайн-конверсии", "Продажи из CRM возвращаются в Метрику и Директ."),
                  ("Дашборд", "Один отчёт: расход, заявки, продажи, ROMI по каналам.")],
        cases=["allo-avto", "pyl-da-zhar"],
        faq=[("Нужна ли CRM?", "Для полной сквозной аналитики — да. Если CRM нет, начнём с Метрики и коллтрекинга и подскажем, какую выбрать."),
             ("Сколько длится настройка?", "Базовая — Метрика, цели, UTM — 2–3 дня. С коллтрекингом и CRM — 1–2 недели.")]),
    "smm": dict(
        title="SMM: ведение сообществ ВКонтакте и Telegram — Регион Маркетинг",
        desc="Ведение сообществ ВКонтакте и Telegram: стратегия, контент-план, посты, оформление. SMM для локального бизнеса с фокусом на продажи.",
        h1="SMM, который <em>продаёт</em>, а не просто постит",
        lead="Ведём сообщества ВКонтакте и каналы в Telegram: стратегия, контент-план, тексты, оформление. Связываем с таргетом, чтобы подписчики превращались в покупателей.",
        kpi=[("ВК + Telegram", "основные площадки"), ("контент-план", "на месяц вперёд"), ("связка", "с таргетом VK Ads")],
        for_whom=["Сообщество есть, но заброшено", "Клиенты спрашивают «а где вас посмотреть?»", "Нужно регулярно рассказывать об акциях и новинках", "Хотите возвращать клиентов на повторные покупки"],
        includes=[("Стратегия", "Рубрики, тон, цели: продажи, доверие, повторные покупки."),
                  ("Оформление", "Обложка, аватар, меню, товары — в фирменном стиле."),
                  ("Контент-план", "На месяц вперёд, согласовываем заранее."),
                  ("Тексты и визуал", "Посты, истории, клипы по готовым материалам."),
                  ("Работа с отзывами", "Собираем и публикуем отзывы — это продаёт лучше рекламы."),
                  ("Отчёт", "Охваты, подписчики, обращения из сообщества.")],
        cases=["pyl-da-zhar", "malina"],
        faq=[("Вы снимаете фото и видео?", "Работаем с вашими материалами и подсказываем, что снять. Съёмку организуем отдельно при необходимости."),
             ("Сколько постов в неделю?", "Обычно 3–5. Частота зависит от ниши — важнее регулярность и польза.")]),
}


def price_block(slug, short):
    d, v, sm, st = PRICES["direct"], PRICES["vk"], PRICES["smm"], PRICES["site"]
    def tiers(fee):
        out, lo = [], 0
        for cap, f in fee:
            out.append(f"<li>Бюджет {'до ' + fmt(cap) if cap < 10**8 else 'от ' + fmt(lo)} — <b>{fmt(f)}/мес</b></li>")
            lo = cap
        return "".join(out)
    cards = {
        "sites": [("Экспресс-сайт", fmt(st["express"]), "Готовый продающий шаблон под нишу, запуск за 3 дня, без правок. Рассрочка от 460 ₽/мес."),
                  ("Продающий лендинг", fmt(st["landing"]), "Прототип под заявки, тексты, дизайн, Метрика и цели. Лучший вариант под рекламу."),
                  ("Магазин / многостраничник", fmt(st["shop"]), "Каталог, корзина, онлайн-оплата, SEO-структура под продвижение.")],
        "direct": [("Настройка", fmt(d["setup"]), f"Семантика, поиск + РСЯ, ретаргетинг, цели. Товарные кампании — +{fmt(d['shopExtra'])}."),
                   ("Ведение", "от " + fmt(d["fee"][0][1]) + "/мес", "<ul class='tiers'>" + tiers(d["fee"]) + "</ul>"),
                   ("Рекламный бюджет", "от 20 000 ₽", "Платите напрямую в Яндекс, в своём кабинете. Нам — только за работу.")],
        "vk-ads": [("Настройка", fmt(v["setup"]), "Аудитории, креативы, лид-формы, пиксель VK и цели."),
                   ("Ведение", "от " + fmt(v["fee"][0][1]) + "/мес", "<ul class='tiers'>" + tiers(v["fee"]) + "</ul>"),
                   ("Рекламный бюджет", "от 15 000 ₽", "Платите напрямую в VK Реклама, в своём кабинете.")],
        "seo": [("Лендинг", "от " + fmt(int(PRICES["seo"]["region"]["local"] * 0.8)) + "/мес", "Локальный бизнес, один город, до 10 страниц."),
                ("Сайт до 50 страниц", "от " + fmt(PRICES["seo"]["region"]["local"]) + "/мес", "Москва и МО — от " + fmt(PRICES["seo"]["region"]["msk"]) + "/мес, вся Россия — от " + fmt(PRICES["seo"]["region"]["rf"]) + "/мес."),
                ("Интернет-магазин", "от " + fmt(int(PRICES["seo"]["region"]["local"] * 1.4)) + "/мес", "Категории, фильтры, карточки товаров, фиды в Яндекс.")],
        "smm": [("3 поста в неделю", fmt(sm["posts"]["3"]) + "/мес", "Контент-план, тексты, визуал, модерация. Оформление сообщества — " + fmt(sm["setup"]) + " разово."),
                ("5 постов в неделю", fmt(sm["posts"]["5"]) + "/мес", "Для ниш с частыми новинками и акциями: цветы, еда, красота."),
                ("Опции", "+" + fmt(sm["telegram"]), "Telegram-канал; клипы и истории — +" + fmt(sm["video"]) + "/мес.")],
        "analytics": [("Базовая", "Бесплатно", "Метрика, цели и UTM — входят в любую услугу."),
                      ("Сквозная", fmt(PRICES["analytics"]) + " разово", "Коллтрекинг, передача заявок в CRM, офлайн-конверсии, дашборд."),
                      ("Сопровождение", "в ведении", "При ведении рекламы отчёт по каналам — каждую неделю.")],
    }[slug]
    html = "".join(f'<div class="card price"><p class="label">{t}</p><p class="price__val">{pr}</p><div class="muted">{x}</div></div>' for t, pr, x in cards)
    calc_btn = (f'<a class="rg-btn rg-btn--primary" href="calculator.html?s={slug}">Рассчитать точно</a>'
                if slug in ("direct", "vk-ads", "seo", "smm") else
                f'<a class="rg-btn rg-btn--primary" href="#lead" data-open-lead data-service="{short}">Получить расчёт</a>')
    return f'''<section class="section" id="price">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Сколько <em>стоит</em></h2>
      {calc_btn}
    </div>
    <div class="grid grid--3">{html}</div>
    <p class="caption" style="margin-top:24px">Скидка на ведение при заказе нескольких каналов: 2 — 5%, 3 — 10%, 4 — 15%. Рассрочка 0% через Т-Банк.</p>
  </div>
</section>'''


def build_service(slug):
    d = SERVICE_PAGES[slug]
    short = next(s[1] for s in SERVICES if s[0] == slug)
    menu = next(s[2] for s in SERVICES if s[0] == slug)
    kpi = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in d["kpi"])
    whom = "".join(f"<li>{x}</li>" for x in d["for_whom"])
    inc = "".join(f'<div class="card"><h3 class="h3">{t}</h3><p class="muted">{x}</p></div>' for t, x in d["includes"])
    cases = "".join(case_card(k) for k in d["cases"])
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in d["faq"])
    body = f'''<section class="page-hero">
  <div class="container">
    <p class="crumbs"><a href="index.html">Главная</a> / <a href="index.html#services">Услуги</a> / {menu}</p>
    <h1 class="rg-headline h1">{d["h1"]}</h1>
    <p class="lead">{d["lead"]}</p>
    <div class="btn-row">
      <a class="rg-btn rg-btn--primary" href="#lead" data-open-lead data-service="{short}">Получить расчёт</a>
      <a class="rg-btn rg-btn--secondary" href="#price">Цены</a>
    </div>
  </div>
</section>

<section class="section--tight section section--ink">
  <div class="container kpi-row">{kpi}</div>
</section>

<section class="section">
  <div class="container split">
    <h2 class="rg-headline h2">Кому <em>подходит</em></h2>
    <ul class="checks">{whom}</ul>
  </div>
</section>

<section class="section section--raised">
  <div class="container">
    <div class="section__head"><h2 class="rg-headline h2">Что <em>входит</em> в работу</h2></div>
    <div class="grid grid--3">{inc}</div>
  </div>
</section>

{price_block(slug, short)}

<section class="section section--raised" id="service-cases">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Результаты <em>клиентов</em></h2>
      <a class="rg-btn rg-btn--secondary" href="cases.html">Все кейсы</a>
    </div>
    <div class="cases">{cases}</div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <h2 class="rg-headline h2">Вопросы <em>по услуге</em></h2>
    <div class="faq">{faq}</div>
  </div>
</section>'''
    page(slug, d["title"], d["desc"], body, preselect=slug)


# ───────────────────────── КЕЙСЫ, КОНТАКТЫ, СЛУЖЕБНЫЕ ─────────────────────────

def build_cases():
    cases = "".join(case_card(k) for k in CASES)
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in STATS)
    body = f'''<section class="page-hero">
  <div class="container">
    <p class="crumbs"><a href="index.html">Главная</a> / Кейсы</p>
    <h1 class="rg-headline h1"><em>97 млн ₽</em> дохода через четыре сайта</h1>
    <p class="lead">Реальные цифры клиентов из локального бизнеса: цветы, доставка еды, автосалон. Считаем деньги, которые принёс сайт, а не лайки и клики.</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container"><div class="cases">{cases}</div></div>
</section>
<section class="section section--ink">
  <div class="container"><div class="stats">{stats}</div></div>
</section>'''
    page("cases", "Кейсы — Регион Маркетинг: сайты и реклама с результатом в рублях",
         "Кейсы агентства «Регион Маркетинг»: 28 млн ₽ через сайт цветочной сети, 35 млн ₽ автосалону за первый месяц, 16% конверсия сайта доставки еды.",
         body, cta_kwargs=dict(title='Хотите <em>такие же цифры</em>?'))


def build_contacts():
    body = f'''<section class="page-hero">
  <div class="container">
    <p class="crumbs"><a href="index.html">Главная</a> / Контакты</p>
    <h1 class="rg-headline h1">Обсудим <em>ваш проект</em></h1>
    <p class="lead">Отвечаем в течение рабочего часа. Удобнее всего — Telegram или звонок.</p>
    <div class="grid grid--4" style="margin-top:48px">
      <a class="card service" href="tel:{CONFIG["phone_raw"]}"><p class="label">Телефон</p><p class="h3">{CONFIG["phone"]}</p></a>
      <a class="card service" href="{CONFIG["telegram"]}" target="_blank" rel="noopener"><p class="label">Telegram</p><p class="h3">Написать →</p></a>
      <a class="card service" href="{CONFIG["whatsapp"]}" target="_blank" rel="noopener"><p class="label">WhatsApp</p><p class="h3">Написать →</p></a>
      <a class="card service" href="mailto:{CONFIG["email"]}"><p class="label">Почта</p><p class="h3" style="word-break:break-all">{CONFIG["email"]}</p></a>
    </div>
    <p class="muted" style="margin-top:32px">{CONFIG["city"]}. {CONFIG["legal"]}.</p>
  </div>
</section>'''
    page("contacts", "Контакты — Регион Маркетинг", "Связаться с агентством «Регион Маркетинг»: телефон, Telegram, WhatsApp, почта. Бесплатный расчёт заявок за 1 день.", body)


def build_simple():
    page("thanks", "Спасибо, заявка принята — Регион Маркетинг", "Заявка принята.", f'''<section class="page-hero">
  <div class="container">
    <h1 class="rg-headline h1">Заявка <em>принята</em></h1>
    <p class="lead">Перезвоним в течение рабочего часа. Пока ждёте — посмотрите, какие результаты получили наши клиенты.</p>
    <div class="btn-row"><a class="rg-btn rg-btn--primary" href="cases.html">Смотреть кейсы</a><a class="rg-btn rg-btn--secondary" href="{CONFIG["telegram"]}">Написать в Telegram</a></div>
  </div>
</section>''', noindex=True, with_cta=False)

    page("404", "Страница не найдена — Регион Маркетинг", "Страница не найдена.", '''<section class="page-hero">
  <div class="container">
    <p class="display" style="color:var(--accent-text)">404</p>
    <h1 class="rg-headline h2" style="margin-top:24px">Такой страницы нет</h1>
    <p class="lead" style="margin-top:16px">Зато есть кейсы и услуги, которые приносят клиентам заявки.</p>
    <div class="btn-row"><a class="rg-btn rg-btn--primary" href="index.html">На главную</a><a class="rg-btn rg-btn--secondary" href="cases.html">Кейсы</a></div>
  </div>
</section>''', noindex=True, with_cta=False)

    page("privacy", "Политика обработки персональных данных — Регион Маркетинг",
         "Политика обработки персональных данных сайта region-studio.ru.", f'''<section class="page-hero">
  <div class="container prose">
    <p class="crumbs"><a href="index.html">Главная</a> / Политика</p>
    <h1 class="h1" style="margin:16px 0 24px">Политика обработки персональных данных</h1>
    <p>Оператор персональных данных — {CONFIG["legal"]} (далее — Оператор). Политика действует в отношении информации, которую Оператор получает от посетителей сайта {CONFIG["domain"]}.</p>
    <h2>Какие данные обрабатываем</h2>
    <p>Имя, номер телефона, адрес сайта или описание ниши, которые вы указываете в форме; технические данные — cookie, IP-адрес, сведения о браузере и источнике перехода (через Яндекс Метрику).</p>
    <h2>Цели обработки</h2>
    <p>Связаться с вами по заявке, подготовить расчёт и коммерческое предложение, заключить и исполнить договор, улучшить работу сайта.</p>
    <h2>Правовое основание</h2>
    <p>Согласие субъекта персональных данных (ст. 6 Федерального закона № 152-ФЗ «О персональных данных»), которое вы даёте, отмечая соответствующее поле в форме.</p>
    <h2>Хранение и передача</h2>
    <p>Данные хранятся на серверах в Российской Федерации не дольше, чем этого требуют цели обработки. Третьим лицам не передаются, кроме случаев, предусмотренных законом.</p>
    <h2>Ваши права</h2>
    <p>Вы можете запросить сведения о своих данных, потребовать их уточнения или удаления и отозвать согласие, написав на {CONFIG["email"]}.</p>
    <p class="caption" style="margin-top:32px">[Проверить у юриста и дополнить реквизитами перед публикацией.]</p>
  </div>
</section>''', with_cta=False)


def build_meta():
    pages = ["", "sites.html", "direct.html", "seo.html", "vk-ads.html", "analytics.html", "smm.html", "calculator.html", "cases.html", "contacts.html"]
    urls = "".join(f"<url><loc>{CONFIG['domain']}/{p}</loc></url>" for p in pages)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /thanks.html\nDisallow: /send.php\n\nSitemap: {CONFIG['domain']}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    build_index()
    for s in SERVICE_PAGES:
        build_service(s)
    build_calculator()
    build_cases()
    build_contacts()
    build_simple()
    build_meta()
    print("OK:", ", ".join(sorted(p.name for p in ROOT.glob("*.html"))))
