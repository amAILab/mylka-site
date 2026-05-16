const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const css = fs.readFileSync(path.join(__dirname, '..', 'final-site.css'), 'utf8');

const checks = [
  ['viewport meta', /<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1">/.test(html)],
  ['mobile quick CTA exists', /<nav class="mobile-bar"[\s\S]*href="tel:\+74950058314"[\s\S]*href="#brief"/.test(html)],
  ['mobile bottom safe area', /body\{padding-bottom:calc\(86px \+ env\(safe-area-inset-bottom\)\)\}/.test(css)],
  ['mobile header compacted', /\.header-inner\{gap:10px;min-height:68px\}/.test(css) && /\.brand small\{display:none\}/.test(css)],
  ['mobile CTA row safe area', /\.mobile-bar\{bottom:calc\(12px \+ env\(safe-area-inset-bottom\)\)\}/.test(css)],
];

let failed = false;
for (const [name, ok] of checks) {
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  if (!ok) failed = true;
}
process.exit(failed ? 1 : 0);
