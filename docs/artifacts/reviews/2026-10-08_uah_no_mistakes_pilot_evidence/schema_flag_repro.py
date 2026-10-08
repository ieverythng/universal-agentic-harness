"""Compact reproduction of the predeclared alternate-boolean schema case."""
import contextlib
import io
import json
import runpy

with contextlib.redirect_stdout(io.StringIO()):
    corpus=runpy.run_path('/tmp/uah-pilot-standards-result/public_probes.py')
observations=corpus['observations']
print(json.dumps([item for item in observations if item['case'] in (
    'schema-additional-flag-False', "schema-additional-flag-'false'"
)],indent=2,default=str))
