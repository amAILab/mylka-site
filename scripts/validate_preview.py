from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
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
        super().__init__(); self.links=[]; self.metas=[]; self.bases=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == 'a' and d.get('href'): self.links.append(d['href'])
        if tag == 'meta': self.metas.append(d)
        if tag == 'base' and d.get('href'): self.bases.append(d['href'])

def is_external(href):
    if href.startswith(('mailto:', 'tel:', '#', 'javascript:')): return True
    u=urlparse(href)
    return bool(u.scheme or u.netloc)

for p in HTML_FILES:
    rel=p.relative_to(ROOT)
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
    # Полную проверку локальных ссылок делаем только для новой ручной страницы.
    # В экспортированном OpenCart много служебных index.php?route=... ссылок,
    # которые штатно переписываются preview-links.js и не должны валить проверку.
    if rel.as_posix() != 'services-step3d.html':
        continue
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
print(f'OK: {len(HTML_FILES)} html files keep noindex/live-base guard; services-step3d local links checked; forbidden legacy wording checked; csv structure warnings: {len(warnings)}')
