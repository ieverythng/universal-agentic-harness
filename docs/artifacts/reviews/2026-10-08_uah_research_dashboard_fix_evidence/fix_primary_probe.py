# Independent review fixture; all mutations are confined to temporary directories.
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path('/home/juanbeck/universal-agentic-harness')
CURRENT = ROOT / 'scripts/render_research_dashboard.py'
BEFORE = ROOT / 'docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/render_research_dashboard.py.before'
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT / 'scripts'))
START = '<!-- research-records:start -->'
END = '<!-- research-records:end -->'

class Parsed(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.tags = []
        self.rows = []
        self.row = None
        self.cell = None
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'tr':
            self.row = []
        if tag == 'td':
            self.cell = ''
    def handle_data(self, value):
        self.text.append(value)
        if self.cell is not None:
            self.cell += value
    def handle_endtag(self, tag):
        if tag == 'td' and self.row is not None:
            self.row.append(self.cell)
            self.cell = None
        if tag == 'tr' and self.row:
            self.rows.append(self.row)
            self.row = None

def fixture(directory, literal='Control', preamble='Reconciled: 2026-10-07.\n', reconciled='2026-10-08', record_date=None, two=True):
    source = directory / 'docs/proposal.md'
    source.parent.mkdir(parents=True)
    source.write_text('Dated historical fact: 2024-02-29.\n')
    entry = dict(id='first', title=literal, kind='proposed_experiment', date=record_date,
                 summary=literal, h_series_dependencies=['H3'],
                 source=dict(path='docs/proposal.md', sha256=hashlib.sha256(source.read_bytes()).hexdigest()), references=[])
    registry = dict(schema_version=1, reconciled_at=reconciled, records=[entry])
    if two:
        registry['records'].append(dict(entry, id='second', title='Control second', summary='Control summary', kind='investigation', h_series_dependencies=['H1']))
    registry_path = directory / 'registry.json'
    registry_path.write_text(json.dumps(registry))
    md = directory / 'docs/research/dashboard.md'
    md.parent.mkdir(parents=True)
    md.write_text('# Review control\n\n' + preamble + '\n## Catalog\n\n' + START + '\n' + END + '\n\n## After\n\nHistorical date: 2024-02-29.\n')
    return registry, registry_path, md, source

def run(script, directory, registry, md, *args):
    return subprocess.run([sys.executable, str(script), '--repo-root', str(directory), '--registry', str(registry), '--markdown', str(md), '--as-of', '2027-01-01', *args], env=ENV, capture_output=True, text=True)

def emit(label, result):
    print(json.dumps(dict(probe=label, **result), ensure_ascii=True))

LITERALS = [
    'A <!-- comment --> B', START, END, '<b>raw</b>', '<script>probe</script>',
    '[label](https://example.invalid)', '& < > " \' ` \\ | * _ # ! - . : ; /',
    '&amp; &#39; &#x3c;',
    'A <!-- c --> [link](javascript:alert(1)) &amp; &#39; | * B',
    '* B | &#39; &amp; [link](javascript:alert(1)) <!-- c --> A',
]
SEPARATORS = ['\n', '\r', '\r\n', '\v', '\f', '\u0085', '\u2028', '\u2029', '\x1c', '\x1d', '\x1e', '\x00', '\x01', '\t']

def literals(script, label):
    failures = []
    for literal in LITERALS + ['First' + s + 'Second' for s in SEPARATORS]:
        with tempfile.TemporaryDirectory(prefix='uah-fix-literal-') as tmp:
            d = Path(tmp)
            registry, rp, md, source = fixture(d, literal=literal)
            source_bytes = source.read_bytes()
            result = run(script, d, rp, md)
            if result.returncode:
                failures.append(dict(literal=literal, exit=result.returncode, error=result.stderr.strip()))
                continue
            markdown = md.read_text()
            page = md.with_suffix('.html').read_text()
            parsed = Parsed()
            parsed.feed(page)
            expected = ' '.join(literal.splitlines())
            check = run(script, d, rp, md, '--check')
            again = run(script, d, rp, md)
            ok = expected in ''.join(parsed.text) and len(parsed.rows) == 2 and all(len(r) == 6 for r in parsed.rows) and markdown.count(START) == 1 and markdown.count(END) == 1 and check.returncode == 0 and again.returncode == 0 and md.read_text() == markdown and md.with_suffix('.html').read_text() == page and source.read_bytes() == source_bytes and not any(t in ('img', 'b') or (t == 'a' and a.get('href', '').startswith('javascript:')) for t, a in parsed.tags)
            if not ok:
                failures.append(dict(literal=literal, exit=result.returncode, check=check.returncode, rows=len(parsed.rows), visible_literal=expected in ''.join(parsed.text), delimiter_counts=[markdown.count(START), markdown.count(END)]))
    emit(label + '-literal-matrix', dict(cases=len(LITERALS)+len(SEPARATORS), failures=failures))

def dates(script, label):
    results = []
    for value in ['2024-02-29', '2025-02-29', '2026-12-31', '2027-01-01', '2026-1-1', ' 2026-10-08', '2026-10-08T23:00:00+02:00']:
        with tempfile.TemporaryDirectory(prefix='uah-fix-date-') as tmp:
            d = Path(tmp)
            registry, rp, md, source = fixture(d, reconciled=value, record_date=None)
            result = run(script, d, rp, md)
            results.append(dict(input=value, exit=result.returncode, error=result.stderr.strip(), dates=[line for line in md.read_text().splitlines() if 'Reconciled:' in line]))
    emit(label + '-date-matrix', dict(results=results))
    for name, preamble in [('single', 'Reconciled: 2026-10-07.\n'), ('historical-fence', 'Reconciled: 2026-10-07.\n\nHistorical example:\n\n```text\nReconciled: 2024-02-29.\n```\n'), ('missing', 'Date unknown.\n'), ('malformed', 'Reconciled: 2026-10-07T23:00:00+02:00.\n')]:
        with tempfile.TemporaryDirectory(prefix='uah-fix-owner-') as tmp:
            d = Path(tmp)
            registry, rp, md, source = fixture(d, preamble=preamble)
            result = run(script, d, rp, md)
            check = run(script, d, rp, md, '--check')
            emit(label + '-date-owner-' + name, dict(exit=result.returncode, check=check.returncode, before=preamble, actual=md.read_text().split(START)[0], source_unchanged=source.read_text() == 'Dated historical fact: 2024-02-29.\n'))

def gates(script, label):
    results = []
    for attack in ['empty', 'one', 'hash', 'missing', 'stale', 'reverse']:
        with tempfile.TemporaryDirectory(prefix='uah-fix-gate-') as tmp:
            d = Path(tmp)
            registry, rp, md, source = fixture(d)
            if attack == 'empty': registry['records'] = []
            if attack == 'one': registry['records'] = registry['records'][:1]
            if attack == 'hash': registry['records'][0]['source'] = dict(path='docs/proposal.md', sha256='0'*64)
            if attack == 'missing': registry['records'][0]['source'] = dict(path='docs/absent.md', sha256='0'*64)
            if attack == 'reverse': registry['records'].reverse()
            rp.write_text(json.dumps(registry))
            before_md = md.read_bytes()
            result = run(script, d, rp, md)
            if attack == 'stale':
                md.with_suffix('.html').write_text('stale')
                result = run(script, d, rp, md, '--check')
            results.append(dict(input=attack, exit=result.returncode, error=result.stderr.strip(), no_write=(md.read_bytes()==before_md and not md.with_suffix('.html').exists()) if attack in ['hash','missing'] else None, stdout=result.stdout.strip()))
    emit(label + '-gates', dict(results=results))

def filters(script, label):
    with tempfile.TemporaryDirectory(prefix='uah-fix-filter-') as tmp:
        d = Path(tmp)
        _, rp, md, _ = fixture(d, literal='First\u2028Second | &#39;')
        result = run(script, d, rp, md)
        page = md.with_suffix('.html').read_text()
        parsed = Parsed()
        parsed.feed(page)
        generated_script = re.findall(r'<script>(.*?)</script>', page, flags=re.S)[-1]
        javascript = '''
const rows = INPUT.map(items => ({hidden:false, textContent:items.join(' '), querySelectorAll:()=>items.map(textContent=>({textContent}))}));
const buttons = ['all', 'investigation', 'proposed_experiment'].map(kind=>({dataset:{kind}, addEventListener(n,f){this[n]=f;}, setAttribute(){}}));
const controls = {querySelectorAll:()=>buttons};
const search = {value:'',addEventListener(n,f){this[n]=f;}};
const gate = {value:'all',addEventListener(n,f){this[n]=f;}};
const count = {textContent:''};
const table = {querySelector:()=>({textContent:'Research record'}),querySelectorAll:()=>rows};
const document = {querySelectorAll:()=>[table],getElementById:id=>({'research-tabs':controls,'research-search':search,'research-gate':gate,'research-count':count}[id])};
eval(SCRIPT);
const output=[];
function record(name){output.push({name,count:count.textContent,visible:rows.filter(r=>!r.hidden).length});}
record('all'); gate.value='H3'; gate.change(); record('H3'); buttons[1].click(); record('investigation+H3');
buttons[0].click(); gate.value='H1';search.value='Control';search.input();record('Control+H1');
buttons[2].click();gate.value='H3';search.value='&#39;';search.input();record('literal-entity+proposal+H3');
console.log(JSON.stringify(output));
'''.replace('INPUT', json.dumps(parsed.rows)).replace('SCRIPT', json.dumps(generated_script))
        result = subprocess.run(['node','-e',javascript], capture_output=True, text=True)
        emit(label+'-filter-script', dict(exit=result.returncode, output=result.stdout.strip(), error=result.stderr.strip(), dom_rows=len(parsed.rows)))

def date_only(script, label):
    with tempfile.TemporaryDirectory(prefix='uah-fix-date-only-') as tmp:
        d = Path(tmp)
        registry, rp, md, source = fixture(d)
        run(script,d,rp,md)
        first_md=md.read_text();first_html=md.with_suffix('.html').read_text()
        registry['reconciled_at']='2026-12-31';rp.write_text(json.dumps(registry))
        result=run(script,d,rp,md)
        second_md=md.read_text();second_html=md.with_suffix('.html').read_text()
        emit(label+'-date-only-delta',dict(exit=result.returncode,md_date_only=second_md.replace('2026-12-31','2026-10-08')==first_md,html_date_only=second_html.replace('2026-12-31','2026-10-08')==first_html,date_visible='Reconciled: 2026-12-31.' in second_md,history_preserved='Historical date: 2024-02-29.' in second_md,source_unchanged=source.read_text()=='Dated historical fact: 2024-02-29.\n'))

def real_catalog(script, label):
    with tempfile.TemporaryDirectory(prefix='uah-fix-real-') as tmp:
        md=Path(tmp)/'dashboard.md'
        md.write_bytes((ROOT/'docs/artifacts/reviews/2026-10-08_uah_research_dashboard_fix_evidence/uah_research_dashboard.md.before').read_bytes())
        rp=ROOT/'docs/research/experiment_registry.json'
        result=run(script,ROOT,rp,md)
        parsed=Parsed();parsed.feed(md.with_suffix('.html').read_text())
        check=run(script,ROOT,rp,md,'--check')
        emit(label+'-real-catalog',dict(exit=result.returncode,check=check.returncode,rows=len(parsed.rows),columns=[len(row) for row in parsed.rows],unknown=sum(row[2]=='unknown' for row in parsed.rows),not_scored=sum(row[4]=='not_scored' for row in parsed.rows),html_sha256=hashlib.sha256(md.with_suffix('.html').read_bytes()).hexdigest()))

def entities(script,label):
    with tempfile.TemporaryDirectory(prefix='uah-fix-entity-') as tmp:
        d=Path(tmp)
        preamble='Reconciled: 2026-10-07.\n\nLiteral code example:\n\n```text\n&#35; &#60; &#39; &amp;\n```\n'
        _,rp,md,_=fixture(d,preamble=preamble)
        result=run(script,d,rp,md)
        parsed=Parsed();parsed.feed(md.with_suffix('.html').read_text())
        emit(label+'-nonmetadata-code-entity',dict(exit=result.returncode,check=run(script,d,rp,md,'--check').returncode,markdown_retains_example='&#35; &#60; &#39; &amp;' in md.read_text(),html_visible_example='&#35; &#60; &#39; &amp;' in ''.join(parsed.text),visible_text=''.join(parsed.text).split('Literal code example:')[1].split('Catalog')[0]))

for script, label in [(CURRENT, 'current'), (BEFORE, 'before')]:
    if '--entities' in sys.argv:
        entities(script,label)
    elif '--focused' in sys.argv:
        filters(script,label)
        date_only(script,label)
        real_catalog(script,label)
    else:
        literals(script, label)
        dates(script, label)
        gates(script, label)
