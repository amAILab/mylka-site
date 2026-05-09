# Mylco static preview clone

Статический рабочий клон сайта https://mylco.ru для аудита и дальнейшей переработки.

Важно:
- это не бэкап CMS/OpenCart и не содержит серверной логики, базы заказов или админки;
- формы, корзина, личный кабинет и checkout в таком виде не должны использоваться как продакшен;
- добавлены `robots.txt` и `noindex`, чтобы публичный preview не конкурировал с текущим сайтом в поиске.

Снято как безопасный статический snapshot для последующего редизайна/переноса.

## Preview / production safety

This repository is a static GitHub Pages preview of an old OpenCart export. It is not a connected production shop.

Current preview requirements:
- keep `meta robots` as `noindex,nofollow`;
- keep `robots.txt` closed with `Disallow: /`;
- keep cart/account/checkout/forms visually and functionally marked as preview-only until backend/CRM is connected.

Before production launch, update:
- robots meta to `index,follow` where appropriate;
- canonical and `og:url` to the production domain;
- `robots.txt` to the production crawl policy;
- form actions / CRM endpoints / cart and checkout integration.

See `AUDIT_FIXES.md` for the current audit notes and remaining risks.
