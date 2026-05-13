from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import csv
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
CSV_FILES = sorted(p for p in ROOT.rglob('*.csv') if '.git' not in p.parts)
SOURCE_FILES = sorted(
    p for pattern in ('*.csv', '*.py')
    for p in ROOT.rglob(pattern)
    if '.git' not in p.parts and p.name != 'validate_preview.py'
)
errors = []
warnings = []

FORBIDDEN_PATTERNS = [
    (re.compile(r'STEP\s*3D|Step3D', re.I), 'direct STEP 3D brand mention'),
    (re.compile(r'базов\w*\s+обучен\w*', re.I), 'training bundle wording'),
    (re.compile(r'мастер[-\s]?класс\w*', re.I), 'master-class wording'),
    (re.compile(r'(?<!без\s)\bкурс(?:ы|ов|ами|ах)?\b', re.I), 'course wording without explicit “без”'),
]

ALLOWED_NEGATIVE_PHRASES = (
    'без курсов и обучения',
    'без обучения и курсов',
    'без обучения',
    'без курсов',
    'не про обучение',
)

def text_without_allowed_negatives(text):
    cleaned = text
    # URL/class compatibility names are allowed; visible copy must stay brand-neutral.
    cleaned = re.sub(r'services-step3d|mylco-step3d', '', cleaned, flags=re.I)
    for phrase in ALLOWED_NEGATIVE_PHRASES:
        cleaned = re.sub(re.escape(phrase), '', cleaned, flags=re.I)
    return cleaned


def check_forbidden_text(rel, text):
    cleaned = text_without_allowed_negatives(text)
    for pattern, label in FORBIDDEN_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            snippet = ' '.join(cleaned[max(0, match.start()-40):match.end()+40].split())
            errors.append(f'{rel}: {label}: {snippet}')
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.link_texts=[]; self.metas=[]; self.bases=[]; self._link_stack=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == 'a' and d.get('href'):
            self.links.append(d['href'])
            self.link_texts.append({'href': d['href'], 'text': ''})
            self._link_stack.append(self.link_texts[-1])
        if tag == 'meta': self.metas.append(d)
        if tag == 'base' and d.get('href'): self.bases.append(d['href'])
    def handle_data(self, data):
        if self._link_stack:
            self._link_stack[-1]['text'] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self._link_stack:
            self._link_stack.pop()

SERVICE_BRIEF_FIELDS = (
    'Нужный результат',
    'CAD / мастер-модель / прототип / малая серия / подбор материала',
    'Задача и цель',
    'Фото/файл/ссылка',
    'Габариты и тираж',
    'Условия применения',
    'Материал выбран или нужен подбор',
    'Город доставки',
    'Нужен счёт для юрлица',
    'Желаемый срок',
    'цена / срок / точность / внешний вид',
)

def require_service_brief(rel, label, href):
    decoded_href = unquote(href)
    for field in SERVICE_BRIEF_FIELDS:
        if field not in decoded_href:
            errors.append(f'{rel}: {label} CTA misses full service brief field: {field}')

SERVICE_CTA_COPY_MARKERS = ('бриф', 'расч')
GENERIC_SERVICE_CTA_LABELS = (
    'обсудить задачу',
    'связаться',
    'контакты',
    'написать',
)

def require_service_cta_copy(rel, label, visible_text):
    normalized = ' '.join(visible_text.lower().split())
    if not any(marker in normalized for marker in SERVICE_CTA_COPY_MARKERS):
        errors.append(f'{rel}: {label} CTA visible text is not tied to brief/calculation: {visible_text}')
    if normalized in GENERIC_SERVICE_CTA_LABELS:
        errors.append(f'{rel}: {label} CTA degraded to generic contact/discussion copy: {visible_text}')

def is_external(href):
    if href.startswith(('mailto:', 'tel:', '#', 'javascript:')): return True
    u=urlparse(href)
    return bool(u.scheme or u.netloc)

for p in HTML_FILES:
    rel=p.relative_to(ROOT)
    rel_posix = rel.as_posix()
    text=p.read_text(errors='ignore')
    check_forbidden_text(rel, text)
    low=text.lower()
    # Some OpenCart agreement exports are HTML fragments loaded into modals, not standalone pages.
    # Enforce robots noindex on real pages only.
    if ('<html' in low or '<head' in low or '<!doctype' in low) and '<meta name="robots" content="noindex' not in low and "<meta name='robots' content='noindex" not in low:
        errors.append(f'{rel}: no noindex robots meta')
    parser=LinkParser(); parser.feed(text)
    for base in parser.bases:
        if base.startswith('https://mylco.ru'):
            errors.append(f'{rel}: base points to live mylco.ru')
    if rel_posix.startswith('generated/product-pages/') and rel.name != 'index.html':
        mailto_links = [href for href in parser.links if href.startswith('mailto:order@mylco.ru')]
        local_source_links = [href for href in parser.links if href.startswith('../../')]
        if not mailto_links:
            errors.append(f'{rel}: generated card has no order@mylco.ru mailto CTA')
        for href in mailto_links:
            decoded_href = unquote(href)
            for required in ('Город доставки', 'Нужен счёт для юрлица', 'Предпочтительный формат результата', 'Нужна мастер-модель/CAD/прототип'):
                if required not in decoded_href:
                    errors.append(f'{rel}: mailto CTA misses required brief field: {required}')
        if not local_source_links:
            errors.append(f'{rel}: generated card has no local source CTA')
        for href in local_source_links:
            clean = href.split('#',1)[0].split('?',1)[0]
            if not (clean.endswith('.html') or clean.endswith('/')):
                errors.append(f'{rel}: source CTA is not a local html/category path: {href}')
            target = (p.parent / clean).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f'{rel}: source CTA escapes preview: {href}')
    # Полную проверку локальных ссылок делаем только для новой ручной страницы.
    # В экспортированном OpenCart много служебных index.php?route=... ссылок,
    # которые штатно переписываются preview-links.js и не должны валить проверку.
    if rel.as_posix() != 'services-step3d.html':
        continue
    service_ctas = {
        'hero': {'href': None, 'text': None},
        'final': {'href': None, 'text': None},
    }
    for item in parser.link_texts:
        href = item['href']
        label = ' '.join(item['text'].split())
        if not href.startswith('mailto:order@mylco.ru'):
            continue
        if label == 'Обсудить задачу по брифу':
            service_ctas['hero'] = {'href': href, 'text': label}
        if label == 'Отправить финальный бриф':
            service_ctas['final'] = {'href': href, 'text': label}
    for label, cta in service_ctas.items():
        if not cta['href']:
            errors.append(f'{rel}: missing {label} full service brief CTA')
        else:
            require_service_brief(rel, label, cta['href'])
            require_service_cta_copy(rel, label, cta['text'])
    for href in parser.links:
        if href.startswith('https://amailab.github.io/mylka-site/'):
            continue
        if is_external(href):
            continue
        clean = href.split('#',1)[0].split('?',1)[0]
        if not clean:
            continue
        target = (p.parent / clean).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f'{rel}: link escapes preview: {href}')
            continue
        if not target.exists():
            errors.append(f'{rel}: missing local link {href}')
for p in SOURCE_FILES:
    rel=p.relative_to(ROOT)
    text=p.read_text(errors='ignore')
    check_forbidden_text(rel, text)

for p in CSV_FILES:
    rel=p.relative_to(ROOT)
    with p.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            source_url = (row.get('source_url') or '').strip()
            extra_fields = row.get(None) or []
            if extra_fields:
                warnings.append(f'{rel}:{line_no}: csv extra fields after header ({len(extra_fields)})')
            if source_url and not re.search(r'(?:^|/|@)[\w%+.-]+(?:\.html|/)$', source_url):
                warnings.append(f'{rel}:{line_no}: source_url is not a local html/category path: {source_url[:80]}')

if errors:
    print('\n'.join(errors[:200]))
    print(f'FAILED: {len(errors)} issue(s)')
    sys.exit(1)
if warnings:
    print('\n'.join(f'WARNING: {w}' for w in warnings[:80]))
    if len(warnings) > 80:
        print(f'WARNING: ... and {len(warnings) - 80} more CSV warning(s)')
print(f'OK: {len(HTML_FILES)} html files keep noindex/live-base guard; services-step3d local links checked; generated card CTAs checked; service brief CTAs checked; service CTA copy checked; forbidden legacy wording checked; csv structure warnings: {len(warnings)}')
