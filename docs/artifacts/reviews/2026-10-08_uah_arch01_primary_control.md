# Independent execute-before-read control

Executed 2026-10-08 16:28 UTC before reading implementation/diff/test source.
Throwaway copies: `/tmp/uah-arch01-primary.qXMxdY/{current,before}`.
Both copies use the same current `tests/test_prompt_compiler.py` and unaffected
source/resources/dependencies. Only exact-before `proposal_admission.py` and
`prompt_compiler.py` replace their counterparts in the before copy.

Current SHA-256:

```text
033ba785928c9019b76711ed27c603b6f3f30a2e3110443875bdfea6af019888 proposal_admission.py
9caaf597a1d08983f53f27672e425ba7971cc2b47e9ce0b099f0fa9ba5121ae1 prompt_compiler.py
c04db4be3abc125e43ace67d4416a412f18c2288da8a30362ae85c199c63774b test_prompt_compiler.py
```

Exact-before SHA-256:

```text
a2a76bf21eb865934d63b5eeece722b4b7827d659421fb7a5bc566bb3161455c proposal_admission.py
c76d829b9e6b9e04c6856fcb35ce6f61e26953f881a27cdd3ef79e1016a34b82 prompt_compiler.py
```

Command, run once per variant from the variant root:

```bash
PYTHONPATH=src /home/juanbeck/universal-agentic-harness/.venv/bin/python -m pytest -q tests/test_prompt_compiler.py
```

Current: exit 0, `26 passed in 0.15s`.
Exact-before: exit 1, `2 failed, 24 passed in 0.18s`.

Failing current-test cases against exact-before:

- `test_prompt_compiler_excludes_an_operation_with_a_forbidden_observable`
- `test_prompt_and_admission_agree_on_task_prohibited_effects[expected1-observed1-prohibited1-False]`

Both failures: semantic admission returns `object_effect_prohibited` while the
exact-before prompt compiler does not raise the expected no-direct-proposal
`ValueError`. No changed source had been read when these results were observed.
The copied test bytecode retains original checkout filenames in pytest tracebacks;
independent probe runs will disable bytecode reuse and report imported file paths.
