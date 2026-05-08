from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import sys
ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
errors = []
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
if errors:
    print('\n'.join(errors[:200]))
    print(f'FAILED: {len(errors)} issue(s)')
    sys.exit(1)
print(f'OK: {len(HTML_FILES)} html files keep noindex/live-base guard; services-step3d local links checked')
