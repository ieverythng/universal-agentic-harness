import ast
from pathlib import Path


CORE = Path(__file__).resolve().parents[1] / 'src' / 'ab_harness'


def test_kernel_does_not_import_the_nao_adapter_package():
    violations = []
    for source_path in CORE.rglob('*.py'):
        tree = ast.parse(source_path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                imported_modules = (node.module,)
            elif isinstance(node, ast.Import):
                imported_modules = tuple(alias.name for alias in node.names)
            else:
                continue
            if any(
                module == 'ab_harness_nao'
                or module.startswith('ab_harness_nao.')
                for module in imported_modules
            ):
                violations.append(source_path.name)

    assert violations == []
