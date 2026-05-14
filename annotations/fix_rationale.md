# Fix Rationale

The correct repair is to enforce the sandbox boundary on the final path
that will be opened, including paths produced by compatibility
fallbacks.

Minimal patch:

```python
fallback_path = self._legacy_snapshot_path(effective_locale)
if fallback_path is None:
    raise
if not self._validate_in_sandbox(fallback_path):
    raise TemplateAccessDenied(fallback_path)
return self._loader.read(fallback_path)
```

This keeps public behavior for valid templates unchanged and preserves
`TemplateNotFoundError` for ordinary missing locales such as `ja_JP`.
It also keeps `_legacy_snapshot_path()` as a pure compatibility helper:
constructing an archive path is allowed internally, but callers must
not treat that path as safe until the sandbox predicate has accepted it.
