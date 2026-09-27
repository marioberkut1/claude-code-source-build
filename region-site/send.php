<?php
// Приём заявок с сайта: отправляет в Telegram и на почту.
// Заполните три константы ниже. Нужен хостинг с PHP 7.4+.

const TG_BOT_TOKEN = '';          // токен бота от @BotFather
const TG_CHAT_ID   = '';          // id чата/канала, куда слать заявки
const MAIL_TO      = '';          // почта для заявок, например hello@region-studio.ru

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }
if (!empty($_POST['website'])) { echo '{"ok":true}'; exit; } // бот заполнил ловушку

function f($k) { return trim(strip_tags($_POST[$k] ?? '')); }

$phone = f('phone');
if (strlen(preg_replace('/\D/', '', $phone)) < 10) { http_response_code(422); echo '{"ok":false,"error":"phone"}'; exit; }

$services = isset($_POST['service']) ? (array)$_POST['service'] : [];
$services = implode(', ', array_map(fn($s) => strip_tags($s), $services));

$lines = [
  'Заявка с сайта region-studio.ru',
  'Имя: ' . f('name'),
  'Телефон: ' . $phone,
  'Услуги: ' . ($services ?: '—'),
  'Бюджет: ' . (f('budget') ?: '—'),
  'Сайт/ниша: ' . (f('site') ?: '—'),
  'Комментарий: ' . (f('comment') ?: '—'),
  'Расчёт из калькулятора: ' . (f('calc') ?: '—'),
  '—',
  'Страница: ' . f('page_title') . ' (' . f('page') . ')',
  'Источник: ' . (f('utm_source') ?: (f('referrer') ?: 'прямой')),
];
foreach (['utm_medium','utm_campaign','utm_content','utm_term','yclid'] as $k) {
  if (f($k) !== '') $lines[] = $k . ': ' . f($k);
}
$text = implode("\n", $lines);

$sent = false;

if (TG_BOT_TOKEN && TG_CHAT_ID) {
  $ch = curl_init('https://api.telegram.org/bot' . TG_BOT_TOKEN . '/sendMessage');
  curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => ['chat_id' => TG_CHAT_ID, 'text' => $text],
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 10,
  ]);
  $res = curl_exec($ch);
  $sent = $res && (json_decode($res, true)['ok'] ?? false);
  curl_close($ch);
}

if (MAIL_TO) {
  $subject = '=?UTF-8?B?' . base64_encode('Заявка с сайта: ' . ($services ?: 'без услуги')) . '?=';
  $headers = "Content-Type: text/plain; charset=UTF-8\r\nFrom: noreply@" . ($_SERVER['HTTP_HOST'] ?? 'localhost');
  $sent = mail(MAIL_TO, $subject, $text, $headers) || $sent;
}

if (!$sent) { http_response_code(500); echo '{"ok":false}'; exit; }
echo '{"ok":true}';
