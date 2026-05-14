# Alternatives Considered

## Alt-A - Tighten the locale regex

Rejecting dots or the `legacy.` prefix blocks the known exploit but
changes the public compatibility surface and leaves the real invariant
unenforced: every opened file must be inside the sandbox.

## Alt-B - Block one archive artifact

Special-casing `locale_snapshot.preprod` or a specific year/quarter is
a brittle deny-list. The hidden tests include a second archive artifact
to catch this.

## Alt-C - Remove `_legacy_snapshot_path`

Deleting the helper masks the symptom by removing compatibility logic.
The task asks for a security fix without changing valid public behavior
or unrelated missing-locale behavior.

## Alt-D - Validate only before the primary read

This is the vulnerable pattern. The primary path is safe, but the
fallback path is different. The fix must be attached to the path that
reaches `FileLoader.read()`.

## Alt-E - Move checks into `FileLoader`

This can be valid in a larger refactor, but it broadens the patch and
requires passing settings into a storage helper that currently has a
small "read bytes" contract. The minimal repair belongs in the service
where the sandbox policy already lives.
