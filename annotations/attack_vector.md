# Attack Vector

Working input:

```
name=invoice
locale=legacy.2024.q3.locale_snapshot.preprod
```

The input contains no slash traversal. It is accepted as a locale-like
token, the primary active-template path passes the sandbox check, and
then the missing primary file triggers the legacy fallback branch.

Fallback resolution:

| Stage | Value |
| --- | --- |
| Primary path | `/app/data/templates/invoice/legacy.2024.q3.locale_snapshot.preprod.html` |
| Validated root | `/app/data/templates` |
| Fallback path | `/app/data/templates_archive/retention/2024/q3/locale_snapshot.preprod.html` |

The archive file contains internal retained-render data and is not
tenant-facing. A secure implementation must reject the fallback path
before it reaches `FileLoader.read()`.
