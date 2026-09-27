# Сайт «Регион Маркетинг» — region-studio.ru

Статический многостраничный сайт на чистом HTML/CSS/JS. Цель — заявки.
Дизайн — по дизайн-системе «Регион Маркетинг»: цвета `#6147FF / #1D1D1E / #F3F3F3`, Gilroy, SVG-логотипы, плашки встык, линия роста.

## Страницы

| Файл | Что |
|---|---|
| `index.html` | Главная: оффер, 6 услуг, 4 кейса, цифры, процесс, FAQ, форма |
| `sites.html`, `direct.html`, `seo.html`, `vk-ads.html`, `analytics.html`, `smm.html` | Страницы услуг |
| `cases.html` | Все кейсы |
| `contacts.html` | Контакты |
| `privacy.html` | Политика ПДн (152-ФЗ) |
| `thanks.html` | «Спасибо» после заявки — цель в Метрике по URL |
| `404.html` | Страница не найдена |

## Как править

Тексты, контакты, кейсы и услуги — в `build.py`, в одном месте. После правки:

```bash
python3 build.py
```

HTML пересоберутся. Руками `.html` не правьте — перезапишутся.

## Перед запуском (заглушки)

1. `build.py` → `CONFIG`: телефон, Telegram, WhatsApp, почта, ИП/ИНН, номер счётчика Метрики.
2. `send.php`: токен Telegram-бота, chat_id, почта для заявок.
3. `privacy.html`: проверить у юриста.

## Заявки

Форма отправляет POST на `send.php` → Telegram + почта. В заявку уходят: услуги, имя, телефон, ниша, страница, UTM-метки, yclid, реферер.
Цели Метрики: `lead`, `open_form`, `click_phone`, `click_telegram`, `click_whatsapp` + визит на `thanks.html`.
Нужен хостинг с PHP 7.4+ (Beget, Timeweb, REG.RU — любой).

## Структура

```
assets/css/style.css   — стили (токены дизайн-системы в :root)
assets/js/main.js      — меню, модалка, маска телефона, отправка формы, UTM
assets/fonts/          — Gilroy woff2 (400–800)
assets/img/            — логотипы SVG, фавикон, скрины кейсов
```
