# DocVault

A small document template management service used by tenants to render
invoice and welcome documents in their preferred locale.

## Layout

```
app/
  api/v1/        HTTP handlers
  services/      Render orchestration
  storage/       Filesystem-backed loader
  models/        Template registry
  core/          Settings + domain errors
data/
  templates/             Tenant-facing templates  (the sandbox)
  templates_archive/     Internal archived snapshots — NOT tenant-facing
tests/                   Regression suite
```

## Running tests

```
pip install -e .
pytest -q
```

## Configuration

`DOCVAULT_DATA_DIR` — override the data root (default: `./data` next to the
package).
