# Mylco preview audit fixes

## Текущий режим

Этот репозиторий — статический GitHub Pages preview старого OpenCart-сайта Mylco. Он нужен для аудита, редизайна и подготовки структуры, а не как production-магазин.

Preview-настройки должны сохраняться до отдельного production-запуска:
- `meta robots`: `noindex,nofollow`;
- `robots.txt`: `Disallow: /`;
- формы/корзина/кабинет/checkout считаются неподключёнными к backend/CRM;
- live `mylco.ru` не меняется из этого репозитория.

## Перед production-запуском заменить

- `meta robots` на `index,follow` на страницах, которые должны индексироваться.
- canonical на боевой production URL.
- `og:url` на production-домен.
- `robots.txt` на разрешающую обход политику.
- Убрать/перенастроить `preview-safety.css` и `preview-safety.js` только после подключения backend/CRM/cart.
- Подтвердить телефоны, e-mail, адрес, реквизиты и условия доставки/оплаты с владельцем.

## Что исправлено в этом спринте

- Добавлен глобальный preview safety layer: `preview-safety.css`, `preview-safety.js`.
- На HTML-страницы добавлен комментарий `PREVIEW MODE` и подключение preview guard.
- Добавлен skip-link «Перейти к содержанию» через JS для доступности.
- На всех формах в preview включён `preventDefault` и понятное сообщение: использовать телефон/e-mail.
- Для полей форм добавляются безопасные `autocomplete`: `name`, `tel`, `email`, `organization`.
- Account/cart/checkout/wishlist/compare/login визуально помечаются как disabled preview и блокируются кликом.
- Live-ссылки на `mylco.ru` помечаются `data-live-link="mylco.ru"`/title через JS, чтобы переход не был незаметным.
- На главной canonical/og:url переведены на GitHub Pages preview при сохранённом `noindex`.
- Добавлены базовые data-event для будущей аналитики: phone/email/request quote/disabled ecommerce.

## Найденные проблемы, требующие подтверждения владельца

- В экспортированных HTML много абсолютных ссылок на `https://mylco.ru/...`; часть можно перевести в относительные, но нужно решить, какие страницы должны остаться live-ссылками.
- В старом OpenCart-экспорте много форм с `action="https://mylco.ru/..."`; в preview они заблокированы JS, но для production нужен backend/CRM endpoint.
- Корзина, checkout, личный кабинет, сравнение, избранное и быстрый заказ присутствуют в DOM старого шаблона, но в preview не должны восприниматься как рабочие.
- Данные товаров в CSV — редакционная заготовка. Точные характеристики, цены, наличие, TDS/SDS и совместимость нужно подтверждать по источникам.
- Повторяющиеся телефоны/e-mail/адрес взяты из текущего экспорта и требуют сверки перед запуском.
- Сезонные или временные тексты о задержках доставки нужно вынести в отдельный актуализируемый блок после редакторской проверки.

## Страницы, требующие ручной вычитки

- `index.html`
- `contact-us.html`
- `dostavka.html`
- `o-nas.html`
- основные категории: `kupit-silikon-v-moskve.html`, `kupit-poliuretan-v-moskve.html`, `epoksidnaya-smola.html`, `zhidkiy-plastik.html`, `vakuumnye-kamery.html`
- `generated/product-pages/*.html`

## Аналитика в старом экспорте

В экспортированных HTML обнаружены старые фрагменты аналитики:
- Google Analytics `UA-35012952-1`;
- Яндекс.Метрика `33197413`;
- `noscript`-пиксели Яндекс.Метрики.

Новые счётчики не подключались. Перед production нужно подтвердить, оставлять ли старые ID или заменить на новые.

## События для будущей аналитики

- `click_phone`
- `click_email`
- `request_quote_submit`
- `material_selection_submit`
- `add_to_cart`
- `quick_order`
- `filter_used`
- `product_opened`
- `tds_download`
- `form_error`

Текущий preview layer уже добавляет часть `data-event`: `phone_click`, `email_click`, `request_quote_click`, `preview_disabled_click`, `add_to_cart`.

## P2-рекомендации

- Подборщик материала по задаче.
- Калькулятор расхода силикона/смолы/полиуретана.
- Матрица совместимости: материал формы × материал заливки × разделитель.
- B2B-кабинет/повтор заказа.
- CRM/1C-интеграция.
- Автоматическое КП по CSV/CRM-данным.
