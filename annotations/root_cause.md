# Root Cause

## CWE-22: Path traversal through a post-validation fallback path

`TemplateRenderService.render()` validates the primary path:

`<templates_dir>/<name>/<locale>.html`

The validator itself uses `os.path.commonpath`, so direct traversal and
sibling-prefix inputs are blocked. The defect is that the service then
catches `TemplateNotFoundError`, derives a legacy archive snapshot path
from the locale token, and opens that fallback path without applying the
same sandbox predicate.

The vulnerable operation is therefore not "bad validation" in
isolation. It is validating one path and reading a different path.

Relevant flow:

1. `_compose_path()` builds an active-template path under
   `Settings.templates_dir`.
2. `_validate_in_sandbox()` accepts that active path.
3. `FileLoader.read()` raises `TemplateNotFoundError`.
4. `_legacy_snapshot_path()` maps a token like
   `legacy.2024.q3.locale_snapshot.preprod` to
   `Settings.archive_dir/retention/2024/q3/locale_snapshot.preprod.html`.
5. The fallback path is read without revalidation.
