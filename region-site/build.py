#!/usr/bin/env python3
"""Сборка статического сайта «Регион Маркетинг».

Шапка, подвал, форма и контакты заданы здесь один раз — правьте CONFIG
и тексты ниже, затем запустите:  python3 build.py
На выходе — готовые .html в этой же папке, заливаются на любой хостинг.
"""
from html import escape
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
      <div><h4>Агентство</h4><ul><li><a href="cases.html">Кейсы</a></li><li><a href="index.html#process">Как работаем</a></li><li><a href="index.html#faq">Вопросы</a></li><li><a href="contacts.html">Контакты</a></li></ul></div>
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
    <h2 class="h3" id="modal-title">Получить расчёт</h2>
    <p class="muted">Перезвоним в течение рабочего часа и за 1 день пришлём прогноз заявок.</p>
    <form class="lead-form" novalidate>
    {form_fields("m")}
    </form>
  </div>
</dialog>'''


def page(slug, title, description, body, active=None, noindex=False, with_cta=True, preselect=None, cta_kwargs=None):
    metrika = ""
    if CONFIG["metrika_id"]:
        mid = CONFIG["metrika_id"]
        metrika = f'''<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return;}}}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({mid},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script><noscript><div><img src="https://mc.yandex.ru/watch/{mid}" style="position:absolute;left:-9999px" alt=""></div></noscript>'''
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    url = CONFIG["domain"] + ("/" if slug == "index" else f"/{slug}.html")
    cfg_js = (f'window.RG_CONFIG={{metrikaId:{CONFIG["metrika_id"] or "null"},formEndpoint:"send.php",thanksPage:"thanks.html",'
              f'phone:"{CONFIG["phone"]}",phoneRaw:"{CONFIG["phone_raw"]}",telegram:"{CONFIG["telegram"]}"}};')
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
</body>
</html>
'''
    (ROOT / f"{slug}.html").write_text(html, encoding="utf-8")


# ───────────────────────── ГЛАВНАЯ ─────────────────────────

HERO_ART = '''<div class="hero__art" aria-hidden="true">
  <svg viewBox="0 0 480 480" preserveAspectRatio="xMidYMid slice">
    <rect x="96" y="0" width="64" height="48" fill="#787878"/>
    <rect x="48" y="48" width="208" height="432" fill="#1d1d1e"/>
    <rect x="160" y="0" width="320" height="480" fill="#6147ff"/>
    <polyline class="growth" stroke="#f3f3f3" points="0,400 72,340 112,412 160,372 208,428 312,168 360,252 400,140 492,40"/>
  </svg>
</div>'''


def build_index():
    services = ""
    for i, (slug, short, menu, desc, ic) in enumerate(SERVICES):
        feat = " service--featured" if slug == "sites" else ""
        services += f'''<a class="card service{feat}" href="{slug}.html">
      <span class="service__icon">{icon(ic)}</span>
      <h3 class="h3">{menu}</h3>
      <p>{desc}</p>
      <span class="service__more">Подробнее {icon("arrow")}</span>
    </a>'''
    stats = "".join(f"<div><b>{v}</b><span>{l}</span></div>" for v, l in STATS)
    cases = "".join(case_card(k) for k in ["botanika", "allo-avto", "pyl-da-zhar", "malina"])
    body = f'''<section class="hero">
  <div class="container hero__grid">
    <div>
      <p class="label">Агентство интернет-маркетинга</p>
      <h1 class="rg-headline display">Делаем <em>продающие сайты</em> и обеспечиваем поток клиентов</h1>
      <p class="lead">Сайт, реклама в Яндексе и VK, SEO и аналитика — одной командой и под одну цель: заявки по понятной цене. Отчитываемся в рублях, а не в кликах.</p>
      <div class="btn-row">
        <a class="rg-btn rg-btn--primary" href="#lead" data-open-lead>Получить расчёт</a>
        <a class="rg-btn rg-btn--secondary" href="#cases">Смотреть кейсы</a>
      </div>
      <div class="hero__facts">
        <div><b>97 млн ₽</b><span>дохода клиентов через наши сайты</span></div>
        <div><b>100+</b><span>проектов</span></div>
        <div><b>с 2009</b><span>года на рынке</span></div>
      </div>
    </div>
    {HERO_ART}
  </div>
</section>

<section class="section section--raised" id="services">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Шесть инструментов, <em>одна цель</em> — заявки</h2>
      <p class="muted">Берём проект целиком или отдельный канал. Каждый инструмент настраиваем на цифру: стоимость заявки и продажи.</p>
    </div>
    <div class="grid grid--3">{services}</div>
  </div>
</section>

<section class="section" id="cases">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Кейсы: <em>деньги</em>, которые сайты заработали клиентам</h2>
      <a class="rg-btn rg-btn--secondary" href="cases.html">Все кейсы</a>
    </div>
    <div class="cases">{cases}</div>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Работаем на результат <em>с 2009 года</em></h2>
    </div>
    <div class="stats">{stats}</div>
  </div>
</section>

<section class="section" id="process">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Как работаем: <em>от заявки до продаж</em></h2>
      <p class="muted">Прозрачно на каждом шаге: вы видите план, сроки и цифры до старта.</p>
    </div>
    <ol class="steps">
      <li><h3 class="h3">Разбор</h3><p>Созвон 30 минут: ниша, средний чек, маржа, текущие каналы. Считаем, какая цена заявки окупается.</p></li>
      <li><h3 class="h3">Расчёт и план</h3><p>За 1 день — прогноз заявок, бюджет и план запуска. Фиксируем сроки и стоимость в договоре.</p></li>
      <li><h3 class="h3">Запуск</h3><p>Сайт — от 3 дней, реклама — от 2 дней после согласования. Сразу ставим Метрику и цели.</p></li>
      <li><h3 class="h3">Рост</h3><p>Еженедельно чистим трафик и тестируем гипотезы. Раз в месяц — отчёт: заявки, цена лида, продажи.</p></li>
    </ol>
  </div>
</section>

<section class="section section--raised">
  <div class="container split">
    <div>
      <h2 class="rg-headline h2">Почему с нами <em>выгоднее</em>, чем со штатным маркетологом</h2>
    </div>
    <ul class="checks">
      <li><b>Один ответственный за весь путь клиента.</b> Сайт, реклама и аналитика не спорят между собой, кто виноват в падении заявок.</li>
      <li><b>Считаем в деньгах.</b> Метрика, цели и коллтрекинг с первого дня — видно, какой канал окупается.</li>
      <li><b>Быстрый запуск.</b> Сайт от 3 дней, первые заявки из Директа — в первую неделю.</li>
      <li><b>Сайт — ваш актив.</b> Домен, аккаунты и доступы оформлены на вас.</li>
      <li><b>Опыт в локальном бизнесе.</b> Цветы, доставка еды, автосалоны, услуги — знаем, как продавать в регионах.</li>
    </ul>
  </div>
</section>

<section class="section" id="faq">
  <div class="container split">
    <h2 class="rg-headline h2">Частые <em>вопросы</em></h2>
    <div class="faq">
      <details><summary>Сколько стоит и от чего зависит цена?</summary><p>Стоимость зависит от ниши, региона и объёма работ. Точную сумму и прогноз заявок присылаем после короткого разбора — за 1 рабочий день, бесплатно.</p></details>
      <details><summary>Когда будут первые заявки?</summary><p>Из Яндекс Директа и VK Ads — обычно в первую неделю после запуска. SEO — накопительный канал: первые позиции через 2–4 месяца, дальше поток растёт без оплаты за клик.</p></details>
      <details><summary>Вы работаете с регионами?</summary><p>Да. Большая часть клиентов — локальный бизнес Подмосковья и регионов: Щёлково, Пушкино, Краснодар. Работаем удалённо по всей России.</p></details>
      <details><summary>Кому принадлежит сайт и рекламные кабинеты?</summary><p>Вам. Домен, Tilda, кабинеты Директа и VK, Метрика — на вашем аккаунте или с передачей доступов.</p></details>
      <details><summary>Можно заказать только одну услугу?</summary><p>Да. Но лучший результат даёт связка: сайт + реклама + аналитика — тогда видно, сколько стоит каждая продажа.</p></details>
    </div>
  </div>
</section>'''
    page("index", "Регион Маркетинг — продающие сайты, Яндекс Директ, SEO и VK Ads",
         "Агентство интернет-маркетинга «Регион Маркетинг»: продающие сайты на Tilda, Яндекс Директ, SEO, VK Ads, SMM и сквозная аналитика. 100+ проектов с 2009 года. Бесплатный расчёт заявок.",
         body)


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
      <a class="rg-btn rg-btn--secondary" href="#service-cases">Смотреть кейсы</a>
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

<section class="section" id="service-cases">
  <div class="container">
    <div class="section__head">
      <h2 class="rg-headline h2">Результаты <em>клиентов</em></h2>
      <a class="rg-btn rg-btn--secondary" href="cases.html">Все кейсы</a>
    </div>
    <div class="cases">{cases}</div>
  </div>
</section>

<section class="section section--raised">
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
    pages = ["", "sites.html", "direct.html", "seo.html", "vk-ads.html", "analytics.html", "smm.html", "cases.html", "contacts.html"]
    urls = "".join(f"<url><loc>{CONFIG['domain']}/{p}</loc></url>" for p in pages)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /thanks.html\nDisallow: /send.php\n\nSitemap: {CONFIG['domain']}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    build_index()
    for s in SERVICE_PAGES:
        build_service(s)
    build_cases()
    build_contacts()
    build_simple()
    build_meta()
    print("OK:", ", ".join(sorted(p.name for p in ROOT.glob("*.html"))))
