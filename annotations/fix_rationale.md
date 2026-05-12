# Fix Rationale

## Patch surface

A single method body in `app/services/template_service.py`:
`TemplateRenderService._validate_in_sandbox`. No other file is touched.

## The fix

```python
def _validate_in_sandbox(self, absolute_path: str) -> bool:
    sandbox_root = self._settings.templates_dir
    candidate = os.path.abspath(absolute_path)
    try:
        common = os.path.commonpath([sandbox_root, candidate])
    except ValueError:
        return False
    return common == sandbox_root
```

## Why `commonpath` and not "append a separator"

`os.path.commonpath` operates on **path components** rather than raw
bytes. For the exploit input it returns `/app/data` (the parent of
both `templates` and `templates_archive`), which is unequal to the
sandbox root, so the check correctly fails.

The naive alternative — appending `os.sep` to the sandbox-root string
and keeping the `startswith` comparison — does fix the sibling-prefix
case, but it has two drawbacks:

1. It special-cases the sandbox root itself (a candidate equal to the
   root, with no trailing separator, would now be rejected).
2. It leaves the predicate as a string-level operation, which behaves
   incorrectly on case-insensitive filesystems (macOS HFS+, Windows
   NTFS) when the sandbox root and the candidate differ only in case.

`commonpath` avoids both problems by virtue of being path-aware on
every supported platform.

## Edge cases handled

| Input                                                               | `commonpath` returns | Result   |
| ------------------------------------------------------------------- | -------------------- | -------- |
| `/app/data/templates/invoice/en_US.html` (legitimate)               | `/app/data/templates` | accept  |
| `/app/data/templates_archive/secret.html` (the exploit)             | `/app/data`           | reject  |
| `/app/data/templates` itself                                        | `/app/data/templates` | accept  |
| `/etc/passwd`                                                       | `/`                   | reject  |
| `""` (empty)                                                        | raises `ValueError`   | reject  |
| Different drive letters on Windows                                  | raises `ValueError`   | reject  |

## What the fix deliberately does NOT do

- It does **not** tighten `_LOCALE_RE`. The regex change would mask
  the symptom for one specific input vector but leave the broken
  predicate in place to be re-exploited by any future code path that
  routes user data into a filesystem path.
- It does **not** introduce extra `os.realpath` / `os.stat` calls,
  so render latency is unchanged.
- It does **not** alter the public API contract of `render` — the
  same exception types are raised for the same logical conditions.
- It does **not** modify the `data/templates_archive` layout, the
  configuration object, or the loader. The defect is in the
  predicate; the fix is in the predicate.

## Trade-offs considered

The strictest possible fix would also forbid the candidate from
**equalling** the sandbox root (i.e. require it to be a strict
descendant). We deliberately accept equality because future
refactors may legitimately want to treat the root directory as a
valid "default template" location. The current behaviour matches
the intent that any reachable file must live *inside* the sandbox,
which includes the root directory itself but excludes everything
outside it.
