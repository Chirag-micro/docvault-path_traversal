# Alternatives Considered (Trap Patches)

The grader must accept the gold patch and reject every entry in this
file. Each alternative below either:
  - fixes a *symptom* without fixing the predicate, or
  - introduces a regression on legitimate inputs, or
  - is logically equivalent to the broken behaviour.

## Alt-A — "Append a trailing separator to the sandbox root"

```python
def _validate_in_sandbox(self, absolute_path: str) -> bool:
    sandbox_root = self._settings.templates_dir + os.sep
    return os.path.abspath(absolute_path).startswith(sandbox_root)
```

**Why it is rejected:**
- A path that *equals* the sandbox root (no trailing separator) is now
  rejected even though it is logically inside the sandbox.
  `test_validator_accepts_legitimate_template_path` catches this when
  the candidate happens to be the directory itself; the strict version
  of that test (with the directory passed verbatim) would fail.
- The predicate remains a string-level operation. On case-insensitive
  filesystems a candidate differing only in case is still misclassified.
- The fix is fragile: a future refactor that drops the trailing
  separator anywhere in the chain reintroduces the bug.

## Alt-B — "Restrict the locale regex"

```python
_LOCALE_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")  # no slash, no dotdot
```

**Why it is rejected:**
- It blocks the current exploit vector but leaves the underlying
  predicate broken. Any *other* caller that builds a filesystem path
  from user data — for example, a future "template alias" feature that
  reads paths from the database — will still be vulnerable.
- It regresses legitimate locale codes that contain a slash (e.g.
  `zh-Hant/TW` legacy BCP-47 storage), changing public behaviour.
- The hidden test `test_validator_rejects_sibling_prefix_directly`
  exercises the predicate in isolation and will fail on this fix
  even though the locale regex is tighter.

## Alt-C — "Switch to `os.path.realpath` and keep `startswith`"

```python
def _validate_in_sandbox(self, absolute_path: str) -> bool:
    real = os.path.realpath(absolute_path)
    return real.startswith(self._settings.templates_dir)
```

**Why it is rejected:**
- `realpath` resolves symlinks but does **not** change the textual
  prefix comparison. The sibling directory `templates_archive` still
  passes the check because the strings still share the prefix
  `/app/data/templates`.
- All five FAIL_TO_PASS tests still fail on this patch.

## Alt-D — "Reject `..` segments after normalisation"

```python
def render(self, name, locale=None):
    if locale and ".." in os.path.normpath(locale).split(os.sep):
        raise InvalidTemplateRequest(...)
    ...
```

**Why it is rejected:**
- `os.path.normpath` collapses `..` *before* the check, so by the time
  this guard runs the `..` segments are already gone — the guard is a
  no-op for the actual exploit input.
- Even if the guard were applied to the *raw* (un-normalised) locale,
  it is still input-layer band-aid that leaves the broken predicate
  intact.

## Alt-E — "Just delete the predicate"

```python
def _validate_in_sandbox(self, absolute_path: str) -> bool:
    return True   # the regex on `name` is already strict enough
```

**Why it is rejected (and obviously so):**
- Strictly worse than the vulnerable code: every traversal escapes,
  including `../../../../etc/passwd`.
- The existing regression test `test_obvious_traversal_blocked` fails
  on this patch.

## Alt-F — "Use a try/except around the file open"

```python
def render(self, name, locale=None):
    try:
        return self._loader.read(absolute_path)
    except (PermissionError, FileNotFoundError):
        raise TemplateAccessDenied(...)
```

**Why it is rejected:**
- The exploit succeeds *because* the archive file exists and is
  readable; there is no `PermissionError`/`FileNotFoundError` to
  catch. The exception handler never fires.
- Treats the symptom as an availability concern when it is actually
  a confidentiality breach.

## Alt-G — "Hash-compare the canonicalised path against an allow-list"

```python
ALLOWED = {hashlib.sha256(p.encode()).hexdigest() for p in <known files>}
def _validate_in_sandbox(self, absolute_path: str) -> bool:
    return hashlib.sha256(absolute_path.encode()).hexdigest() in ALLOWED
```

**Why it is rejected:**
- Allow-listing every legitimate `(name, locale)` combination breaks
  the templating model — the whole point of the system is that
  tenants can render any registered template in any registered locale
  without server-side enumeration.
- This is over-engineering that breaks `test_render_explicit_locale`,
  `test_render_welcome_default`, and similar tests.

## Summary

The grader is configured to look for the **predicate-level** fix
specifically. A patch that touches only `_validate_in_sandbox` and
makes the FAIL_TO_PASS tests pass while the PASS_TO_PASS tests
continue to pass is accepted. Any other patch surface — input regex,
loader, handler, configuration — is treated as a trap and rejected.
