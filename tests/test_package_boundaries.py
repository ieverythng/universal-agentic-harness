import ast
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


CORE = Path(__file__).resolve().parents[1] / 'src' / 'ab_harness'
REPO_ROOT = CORE.parents[1]
REMOVED_CORE_MODULES = {
    'nao_h0.py',
    'qualification.py',
    'smoke.py',
    'task_lifecycle_store.py',
    'trace.py',
}


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


def test_wheel_excludes_removed_core_modules_from_a_stale_build_tree(tmp_path):
    project = tmp_path / 'project'
    project.mkdir()
    for filename in ('README.md', 'package.xml', 'pyproject.toml', 'setup.py'):
        shutil.copy2(REPO_ROOT / filename, project / filename)
    shutil.copytree(REPO_ROOT / 'resource', project / 'resource')
    shutil.copytree(REPO_ROOT / 'src', project / 'src')

    stale_core = project / 'build' / 'lib' / 'ab_harness'
    stale_core.mkdir(parents=True)
    for filename in REMOVED_CORE_MODULES:
        (stale_core / filename).write_text('STALE = True\n', encoding='utf-8')

    wheelhouse = tmp_path / 'wheelhouse'
    subprocess.run(
        (
            sys.executable,
            '-m',
            'pip',
            'wheel',
            '.',
            '--no-deps',
            '--no-build-isolation',
            '--wheel-dir',
            str(wheelhouse),
        ),
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    )

    [wheel] = wheelhouse.glob('*.whl')
    with ZipFile(wheel) as archive:
        core_modules = {
            Path(name).name
            for name in archive.namelist()
            if name.startswith('ab_harness/') and name.endswith('.py')
        }

    assert core_modules.isdisjoint(REMOVED_CORE_MODULES)
