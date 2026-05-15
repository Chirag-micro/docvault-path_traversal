# Fix Rationale

The correct repair is to enforce the sandbox boundary inside the helper
that resolves compatibility fallback paths, so it never returns an
out-of-sandbox archive path to callers.

Minimal patch:

```python
resolved = os.path.normpath(os.path.abspath(joined))
if not self._validate_in_sandbox(resolved):
    return None
return resolved
```

This keeps public behavior for valid templates unchanged and preserves
`TemplateNotFoundError` for ordinary missing locales such as `ja_JP`.
It keeps `_legacy_snapshot_path()` as a safe compatibility helper:
constructing a candidate archive path is allowed internally, but the
helper returns `None` unless the resolved path remains inside the public
template sandbox.
