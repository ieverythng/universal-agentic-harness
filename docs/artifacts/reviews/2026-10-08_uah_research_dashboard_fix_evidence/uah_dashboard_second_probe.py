from pathlib import Path
import copy
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
import subprocess
import sys
import tempfile

ROOT = Path('/home/juanbeck/universal-agentic-harness')
SCRIPT = ROOT / 'scripts/render_research_dashboard.py'
WORK = Path(tempfile.mkdtemp(prefix='uah-dashboard-second-'))
(WORK / 'docs/research').mkdir(parents=True)
(WORK / 'docs/source.md').write_text('Proposal only. No measurements.\n')
MD = WORK / 'docs/research/dashboard.md'
REG = WORK / 'registry.json'
SOURCE = WORK / 'docs/source.md'
SKELETON = '# Research dashboard\n\nReconciled: 2026-10-08.\n\n<!-- research-records:start -->\n<!-- research-records:end -->\n'
record = {'id': 'alpha', 'title': 'Alpha', 'kind': 'investigation', 'date': '2026-10-08', 'summary': 'Unique summary needle.', 'h_series_dependencies': ['H0'], 'source': {'path': 'docs/source.md', 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}, 'references': []}
BASE = {'schema_version': 1, 'reconciled_at': '2026-10-08', 'records': [record]}
results = []

def invoke(registry, expected, name, args=(), raw=None):
    MD.write_text(SKELETON)
    MD.with_suffix('.html').unlink(missing_ok=True)
    REG.write_text(json.dumps(registry) if raw is None else raw)
    command = [sys.executable, str(SCRIPT), '--repo-root', str(WORK), '--registry', str(REG), '--markdown', str(MD), '--as-of', '2026-10-08', *args]
    result = subprocess.run(command, capture_output=True, text=True)
    preserved = MD.read_text() == SKELETON and not MD.with_suffix('.html').exists()
    row = {'name': name, 'expected_exit': expected, 'actual_exit': result.returncode, 'stderr': result.stderr.strip(), 'rejection_preserves_outputs': preserved if expected else None}
    results.append(row)
    return result

invoke(BASE, 0, 'canonical')
for name, mutation in [
    ('extra_metric_record', lambda r: r['records'][0].update(metrics={'success_rate': 1})),
    ('extra_status', lambda r: r['records'][0].update(status='approved')),
    ('extra_metric_root', lambda r: r.update(metrics={'latency_ms': 0})),
    ('duplicate_ids', lambda r: r['records'].append(copy.deepcopy(r['records'][0]))),
    ('unknown_kind', lambda r: r['records'][0].update(kind='approved')),
    ('uppercase_kind', lambda r: r['records'][0].update(kind='INVESTIGATION')),
    ('combined_future_bad_hash', lambda r: (r['records'][0].update(date='2026-10-09'), r['records'][0]['source'].update(sha256='0'*64))),
    ('nonleap_day', lambda r: r['records'][0].update(date='2026-02-29')),
    ('datetime_zone', lambda r: r['records'][0].update(date='2026-10-08T00:00:00+02:00')),
    ('date_no_unit', lambda r: r['records'][0].update(date=20261008)),
    ('future_reconcile', lambda r: r.update(reconciled_at='2026-10-09')),
    ('record_after_reconcile', lambda r: r.update(reconciled_at='2026-10-07')),
    ('missing_source', lambda r: r['records'][0]['source'].update(path='docs/absent.md')),
    ('traversal_source', lambda r: r['records'][0]['source'].update(path='docs/../docs/source.md')),
    ('absolute_source', lambda r: r['records'][0]['source'].update(path=str(SOURCE))),
    ('wrong_hash', lambda r: r['records'][0]['source'].update(sha256='0'*64)),
    ('uppercase_hash', lambda r: r['records'][0]['source'].update(sha256=r['records'][0]['source']['sha256'].upper())),
    ('missing_hash', lambda r: r['records'][0]['source'].update(sha256=None)),
    ('duplicate_dependencies', lambda r: r['records'][0].update(h_series_dependencies=['H0', 'H0'])),
    ('nested_nonstring_dependency', lambda r: r['records'][0].update(h_series_dependencies=[{}])),
    ('missing_reference', lambda r: r['records'][0].update(references=['docs/missing.md'])),
]:
    r = copy.deepcopy(BASE)
    mutation(r)
    invoke(r, 1, name)
raw = json.dumps(BASE).replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1')
invoke(BASE, 1, 'duplicate_json_key', raw=raw)
(WORK / 'docs/escape.md').symlink_to('/etc/hosts')
r = copy.deepcopy(BASE)
r['records'][0]['source']['path'] = 'docs/escape.md'
invoke(r, 1, 'symlink_outside')
for kind in ['investigation', 'proposed_experiment', 'executed_probe', 'reviewed_outcome', 'h_series_dependency']:
    r = copy.deepcopy(BASE)
    r['records'][0]['kind'] = kind
    invoke(r, 0, 'kind_' + kind)
for day in ['2024-02-29', '2025-12-31', '2026-01-01', None]:
    r = copy.deepcopy(BASE)
    r['records'][0]['date'] = day
    invoke(r, 0, 'valid_date_' + str(day))
for n in [0, 2, 20]:
    r = copy.deepcopy(BASE)
    r['records'] = [dict(copy.deepcopy(record), id=f'record-{i}', title=f'Record {i}') for i in range(n)]
    invoke(r, 0, f'count_{n}')
    if n == 2:
        r['records'].reverse()
        invoke(r, 0, 'two_reverse_order')
invoke(BASE, 0, 'equals_cli', ['--as-of=20261008'])

# Reconciliation metadata is a separately authored copy in the dashboard header.
invoke(BASE, 0, 'reconciliation_prepare')
r = copy.deepcopy(BASE)
r['reconciled_at'] = '2026-10-09'
REG.write_text(json.dumps(r))
command = [sys.executable, str(SCRIPT), '--repo-root', str(WORK), '--registry', str(REG), '--markdown', str(MD), '--as-of', '2026-10-09', '--check']
res = subprocess.run(command, capture_output=True, text=True)
results.append({'name': 'changed_reconciliation', 'command': command, 'expected': 'check detects stale Reconciled label', 'actual_exit': res.returncode, 'visible_header': MD.read_text().splitlines()[2], 'registry_reconciled_at': r['reconciled_at']})

# Literal display and active-HTML tests use a parser, not visual/browser claims.
r = copy.deepcopy(BASE)
r['records'][0]['title'] = 'A [bracket] *star* `tick` | pipe </script>'
r['records'][0]['summary'] = '<img src=x onerror=alert(1)> [x](javascript:alert(1))'
invoke(r, 0, 'escaping')
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.active=[]
    def handle_data(self, data): self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag == 'img' or (tag == 'a' and dict(attrs).get('href', '').startswith('javascript:')): self.active.append((tag, attrs))
p = Text(); p.feed(MD.with_suffix('.html').read_text())
text = ''.join(p.parts)
results.append({'name': 'literal_title', 'expected_title': r['records'][0]['title'], 'title_preserved': r['records'][0]['title'] in text, 'encoded_bracket_visible': '&#91;' in text, 'active_payload': p.active})

# Real input: same render using registry metadata and existing prose.
real = json.loads((ROOT / 'docs/research/experiment_registry.json').read_text())
page = (ROOT / 'docs/research/uah_research_dashboard.html').read_text()
results.append({'name': 'actual_catalog_counts', 'records': len(real['records']), 'not_scored_cells': page.count('<td>not_scored</td>'), 'source_links': page.count('>Read source</a>'), 'summary_ids': sum(('Catalog ID: <code>'+r['id']+'</code>') in page for r in real['records'])})

# Exact-before generic renderer compared on the same current documentation.
spec = importlib.util.spec_from_file_location('before', '/tmp/uah-research-dashboard-before-20261008/render_agentic_harness_docs.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
mod.ROOT = ROOT; mod.RENDERER = ROOT / 'scripts/render_markdown_html.py'
results.append({'name': 'exact_before_generic_check', 'exit': mod.main(['--check'])})
for path in ['scripts/render_research_dashboard.py', 'tests/test_research_dashboard.py', 'docs/research/experiment_registry.json']:
    result = subprocess.run(['git', 'cat-file', '-e', '28fab5e:'+path], cwd=ROOT, capture_output=True, text=True)
    results.append({'name': 'base_api_exists', 'path': path, 'exit': result.returncode})
print(json.dumps({'work': str(WORK), 'results': results}, indent=2))

for separator in ['\u2028', '\u2029', '\u0085', '\v', '\f']:
    r = copy.deepcopy(BASE)
    r['records'][0]['title'] = 'First' + separator + 'Second'
    invoke(r, 0, 'line_separator_' + hex(ord(separator)))
    page = MD.with_suffix('.html').read_text()
    import re
    counts = [len(re.findall(r'<td>', row)) for row in re.findall(r'<tbody>(.*?)</tbody>', page, re.S)]
    print(json.dumps({'separator': hex(ord(separator)), 'expected_table_cells': 6, 'actual_table_cells': counts, 'html': str(MD.with_suffix('.html'))}))
