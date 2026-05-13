#!/usr/bin/env python3
"""Generate Mylco product preview pages from data/mylco_products_template.csv.

Safe preview generator:
- keeps generated pages noindex/nofollow;
- skips draft/hidden/no_page rows;
- writes static HTML to generated/product-pages/;
- does not touch live mylco.ru.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "mylco_products_template.csv"
OUT_DIR = ROOT / "generated" / "product-pages"


def esc(value: str | None) -> str:
    return html.escape((value or "").strip(), quote=True)


def split_items(value: str | None) -> list[str]:
    if not value:
        return []
    raw = value.replace(",", ";").split(";")
    return [item.strip() for item in raw if item.strip()]


def list_html(items: list[str]) -> str:
    if not items:
        return "<p class=\"muted\">Уточняется под задачу.</p>"
    return "<ul class=\"list\">" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


SOURCE_URL_BY_SLUG = {
    # CSV пока содержит несколько неэкранированных запятых в текстовых полях.
    # Эти безопасные fallback-адреса не дают кнопке «Открыть исходную страницу»
    # уехать в FAQ/ограничения при повторной генерации preview.
    "poly-00-40a-10kg": "kupit-poliuretan-v-moskve/poliuretan-prepolimer-poly-00-40a-10-kg.html",
    "silikon-dlya-form-gips-smola": "kupit-silikon-v-moskve/",
    "vakuumnaya-kamera-h250d210-nasos": "vakuumnaya-kamera-s-nasosom/vakuumnaya-kamera-h250d210-c-nasosom-zsn-1s.html",
    "epoxy-clear-casting": "epoksidnaya-smola.html",
    "liquid-plastic-small-series": "zhidkiy-plastik.html",
    "release-agent-sealer-kit": "razdelitelnye-agenty-i-germetiki.html",
    "pigments-additives-kit": "dobavki-k-epoksidnoy-smole.html",
    "silicone-decor-small-molds": "kupit-silikon-v-moskve/",
    "vacuum-degassing-kit": "vakuumnye-kamery.html",
    "b2b-workshop-material-kit": "contact-us.html",
}


def source_url_for(row: dict[str, str]) -> str:
    """Return a safe local source URL for the secondary product CTA."""
    slug = (row.get("slug") or "").strip()
    source_url = (row.get("source_url") or "").strip()
    if source_url.endswith(".html") or source_url.endswith("/"):
        return source_url
    return SOURCE_URL_BY_SLUG.get(slug, "index.html")


def mailto(row: dict[str, str]) -> str:
    subject = quote(f"Mylco: подбор — {row.get('product_name','товар')}")
    body = quote(
        "Задача:\n"
        "Фото/эскиз:\n"
        "Размеры:\n"
        "Тираж/объём:\n"
        "Срок:\n"
        "Условия эксплуатации:\n"
        "Нужна мастер-модель/CAD/прототип: да/нет\n"
        f"Интересует: {row.get('product_name','')}\n"
    )
    return f"mailto:order@mylco.ru?subject={subject}&body={body}"


def render(row: dict[str, str]) -> str:
    product = row.get("product_name", "Товар Mylco").strip() or "Товар Mylco"
    title = row.get("seo_title") or row.get("hero_title") or product
    desc = row.get("seo_description") or row.get("short_description") or "Mylco: подбор материала, добавок и оборудования под задачу."
    hero_title = row.get("hero_title") or product
    source_url = source_url_for(row)
    source_href = "../../" + source_url
    category = row.get("category", "Материалы")
    subcategory = row.get("subcategory", "")
    benefits = split_items(row.get("key_benefits"))
    limitations = split_items(row.get("limitations"))
    what = split_items(row.get("what_to_send"))
    related = split_items(row.get("related_products"))
    compat = split_items(row.get("materials_compatibility"))
    faq1q = row.get("faq_1_q", "Как понять, подходит ли материал?")
    faq1a = row.get("faq_1_a", "Лучше прислать фото, размеры и условия эксплуатации — Mylco подберёт материал и комплектующие.")
    faq2q = row.get("faq_2_q", "Можно ли подобрать комплект?")
    faq2a = row.get("faq_2_a", "Да, можно подобрать материал, разделитель, добавки и вакуумное решение под задачу.")

    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"robots\" content=\"noindex, nofollow\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{esc(title)}</title>
  <meta name=\"description\" content=\"{esc(desc)}\">
  <style>
    :root{{--ink:#13251d;--deep:#0d2a20;--green:#23b86a;--mint:#eaf8f0;--soft:#f6f4ef;--line:#dbe7de;--muted:#607168;--shadow:0 20px 56px rgba(13,42,32,.10)}}
    *{{box-sizing:border-box}}body{{margin:0;font-family:Arial,Helvetica,sans-serif;color:var(--ink);background:var(--soft);line-height:1.5}}a{{color:inherit}}.wrap{{max-width:1120px;margin:0 auto;padding:32px 18px}}.crumbs{{font-size:13px;color:var(--muted);margin-bottom:14px}}.hero{{display:grid;grid-template-columns:minmax(0,1.16fr) minmax(300px,.84fr);gap:18px;align-items:stretch}}.hero-main,.card{{background:#fff;border:1px solid var(--line);border-radius:28px;padding:26px;box-shadow:var(--shadow)}}.hero-main{{background:radial-gradient(circle at 85% 15%,rgba(141,232,173,.30),transparent 30%),linear-gradient(135deg,#0d2a20,#168850);color:#fff}}.eyebrow,.tag{{display:inline-flex;border-radius:999px;padding:7px 10px;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.04em}}.eyebrow{{border:1px solid rgba(255,255,255,.25);color:#dfffee}}.tag{{background:var(--mint);color:#11864d}}h1{{font-size:clamp(34px,5vw,58px);line-height:1;margin:18px 0 14px;letter-spacing:-.055em}}h2{{font-size:28px;line-height:1.1;letter-spacing:-.04em;margin:12px 0}}h3{{font-size:20px;margin:10px 0 8px}}.lead{{font-size:19px;color:rgba(255,255,255,.9);max-width:760px}}.actions{{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}}.btn{{display:inline-flex;align-items:center;justify-content:center;border-radius:15px;padding:14px 18px;text-decoration:none;font-weight:900}}.btn-main{{background:#fff;color:var(--deep)}}.btn-ghost{{background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.24)}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:16px}}.trust-strip{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}}.trust-item{{background:#fff;border:1px solid var(--line);border-radius:20px;padding:16px;box-shadow:var(--shadow)}}.trust-item b{{display:block;color:var(--deep);margin-bottom:4px}}.trust-item span{{color:var(--muted)}}.list{{margin:0;padding-left:19px}}.list li{{margin:6px 0}}.muted{{color:var(--muted)}}.brief{{background:var(--deep);color:#fff;border-radius:26px;padding:24px;margin-top:16px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px;align-items:center}}.brief p{{color:rgba(255,255,255,.82)}}.brief .btn{{background:var(--green);color:var(--deep)}}.facts{{display:grid;gap:10px;margin-top:12px}}.fact{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid var(--line);padding:9px 0}}.fact b{{color:var(--deep)}}details{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:14px 16px;margin-top:10px}}summary{{font-weight:900;cursor:pointer}}@media(max-width:760px){{.wrap{{padding:18px 14px}}.hero,.grid,.brief,.trust-strip{{grid-template-columns:1fr}}.hero-main,.card{{border-radius:22px;padding:20px}}h1{{font-size:36px}}.lead{{font-size:16px}}.btn{{width:100%}}}}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <div class=\"crumbs\">Mylco / {esc(category)}{(' / ' + esc(subcategory)) if subcategory else ''}</div>
    <section class=\"hero\">
      <div class=\"hero-main\">
        <span class=\"eyebrow\">{esc(category)} · Mylco</span>
        <h1>{esc(hero_title)}</h1>
        <p class=\"lead\">{esc(row.get('short_description'))}</p>
        <div class=\"actions\">
          <a class=\"btn btn-main\" href=\"{mailto(row)}\">Подобрать под задачу</a>
          <a class=\"btn btn-ghost\" href=\"{esc(source_href)}\">Открыть исходную страницу</a>
        </div>
      </div>
      <aside class=\"card\">
        <span class=\"tag\">Быстрый подбор</span>
        <h2>Что прислать</h2>
        {list_html(what)}
        <div class=\"facts\">
          <div class=\"fact\"><span>Фасовка</span><b>{esc(row.get('package_weight') or 'уточнить')}</b></div>
          <div class=\"fact\"><span>Наличие</span><b>{esc(row.get('availability') or 'уточнить')}</b></div>
          <div class=\"fact\"><span>Твёрдость</span><b>{esc(row.get('shore_or_hardness') or 'подбирается')}</b></div>
        </div>
      </aside>
    </section>

    <section class=\"trust-strip\" aria-label=\"B2B и доверие\">
      <div class=\"trust-item\"><b>Счёт для юрлица</b><span>Можно начать с задачи или списка позиций — Mylco соберёт комплект и подготовит расчёт.</span></div>
      <div class=\"trust-item\"><b>Подбор без гадания</b><span>Материал, разделитель, добавки и вакуум подбираются под геометрию, тираж и условия работы.</span></div>
      <div class=\"trust-item\"><b>Маршрут к результату</b><span>Если не хватает модели или образца, подключаются производственные услуги Mylco: CAD, мастер-модель или прототип.</span></div>
    </section>

    <section class=\"grid\">
      <div class=\"card\"><span class=\"tag\">Применение</span><h2>Где использовать</h2><p>{esc(row.get('main_use'))}</p>{list_html(compat)}</div>
      <div class=\"card\"><span class=\"tag\">Плюсы</span><h2>Почему берут</h2>{list_html(benefits)}</div>
      <div class=\"card\"><span class=\"tag\">Ограничения</span><h2>Где проверить</h2>{list_html(limitations)}</div>
    </section>

    <section class=\"grid\">
      <div class=\"card\"><span class=\"tag\">Комплект</span><h2>С чем часто берут</h2>{list_html(related)}</div>
      <div class=\"card\"><span class=\"tag\">FAQ</span><details open><summary>{esc(faq1q)}</summary><p>{esc(faq1a)}</p></details><details><summary>{esc(faq2q)}</summary><p>{esc(faq2a)}</p></details></div>
      <div class=\"card\"><span class=\"tag\">Важно</span><h2>Не гадать по названию</h2><p class=\"muted\">Материал выбирается под геометрию, нагрузку, температуру, тираж и требования к поверхности. Если сомневаетесь — начните с фото и размеров.</p></div>
    </section>

    <section class=\"brief\">
      <div><h2>Сомневаетесь в материале?</h2><p>Mylco предложит материал, разделитель, добавки и вакуумное решение. Если нужна мастер-модель или прототип, можно подключить производственные услуги Mylco: CAD, мастер-модель или прототип.</p></div>
      <a class=\"btn\" href=\"{mailto(row)}\">Отправить задачу</a>
    </section>
  </main>
</body>
</html>
"""


def render_index(rows: list[dict[str, str]]) -> str:
    cards = []
    for row in rows:
        slug = (row.get("slug") or row.get("product_name") or "product").strip()
        safe_slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in slug.lower()).strip("-")
        cards.append(f"""
        <a class=\"item\" href=\"{esc(safe_slug)}.html\">
          <small>{esc(row.get('page_type'))} · priority {esc(row.get('priority'))}</small>
          <b>{esc(row.get('product_name'))}</b>
          <span>{esc(row.get('category'))}{(' / ' + esc(row.get('subcategory'))) if row.get('subcategory') else ''}</span>
          <em>{esc(row.get('short_description'))}</em>
        </a>""")
    cards_html = "\n".join(cards) or "<p>Нет активных карточек.</p>"
    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"robots\" content=\"noindex, nofollow\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Mylco — автосгенерированные карточки товаров</title>
  <style>
    :root{{--ink:#13251d;--deep:#0d2a20;--green:#23b86a;--mint:#eaf8f0;--soft:#f6f4ef;--line:#dbe7de;--muted:#607168;--shadow:0 18px 48px rgba(13,42,32,.09)}}
    *{{box-sizing:border-box}}body{{margin:0;font-family:Arial,Helvetica,sans-serif;color:var(--ink);background:var(--soft);line-height:1.5}}.wrap{{max-width:1120px;margin:0 auto;padding:34px 18px}}.hero{{background:linear-gradient(135deg,#0d2a20,#168850);color:#fff;border-radius:30px;padding:30px;box-shadow:var(--shadow)}}h1{{font-size:clamp(34px,5vw,58px);line-height:1;margin:0 0 12px;letter-spacing:-.055em}}.hero p{{max-width:760px;color:rgba(255,255,255,.84);font-size:18px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px}}.item{{display:flex;flex-direction:column;gap:8px;min-height:220px;background:#fff;border:1px solid var(--line);border-radius:24px;padding:20px;text-decoration:none;color:var(--ink);box-shadow:var(--shadow);transition:.18s ease}}.item:hover{{transform:translateY(-2px);border-color:#9bddb6}}.item small{{align-self:flex-start;background:var(--mint);color:#11864d;border-radius:999px;padding:6px 9px;font-weight:900;text-transform:uppercase;font-size:11px}}.item b{{font-size:22px;line-height:1.1;letter-spacing:-.035em}}.item span{{color:var(--muted);font-weight:800}}.item em{{font-style:normal;color:var(--muted);margin-top:auto}}.note{{margin-top:18px;color:var(--muted)}}@media(max-width:760px){{.wrap{{padding:18px 14px}}.hero{{border-radius:22px;padding:22px}}.grid{{grid-template-columns:1fr}}}}
  </style>
</head>
<body>
  <main class=\"wrap\">
    <section class=\"hero\">
      <h1>Автосгенерированные карточки Mylco</h1>
      <p>Preview-индекс для проверки страниц, собранных из CSV. Все страницы закрыты от индексации и не заменяют живой каталог mylco.ru.</p>
    </section>
    <section class=\"grid\">
      {cards_html}
    </section>
    <p class=\"note\">Источник: <code>data/mylco_products_template.csv</code>. Генератор: <code>scripts/generate_product_pages.py</code>.</p>
  </main>
</body>
</html>
"""


def should_generate(row: dict[str, str]) -> bool:
    status = row.get("status", "").strip().lower()
    page_type = row.get("page_type", "").strip().lower()
    return status == "active" and page_type not in {"", "no_page"}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    generated_rows = []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not should_generate(row):
                continue
            slug = (row.get("slug") or row.get("product_name") or "product").strip()
            safe_slug = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in slug.lower()).strip("-")
            out = OUT_DIR / f"{safe_slug}.html"
            out.write_text(render(row), encoding="utf-8")
            generated.append(out)
            generated_rows.append(row)
    index_path = OUT_DIR / "index.html"
    index_path.write_text(render_index(generated_rows), encoding="utf-8")
    generated.insert(0, index_path)
    print(f"Generated {len(generated) - 1} pages + index:")
    for path in generated:
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
