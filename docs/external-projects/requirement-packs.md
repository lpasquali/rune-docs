# Requirement pack authoring

## Built-in pack ids

**`rune_audit.sr2.packs`** defines stable pack constants. Today the full **IEC 62443 SR-2** catalog is exposed as **`IEC_62443_SR2`**: all ids **`SR-Q-001`** … **`SR-Q-036`**.

`ids_for_pack(pack_id)` is reserved for future named subsets (e.g. SLSA-only, CIS mapping). The parameter is accepted but currently returns the full SR-Q set.

## Authoring new packs (future)

Planned workflow (see **EPIC #229**):

1. Declare a named pack as a **frozen set** of SR-Q ids.
2. Wire **`rune-audit sr2 verify --pack <id>`** when the CLI gains pack filtering.
3. Document evidence expectations per id in **[Quantitative security requirements](../architecture/QUANTITATIVE_SECURITY_REQUIREMENTS.md)**.

## Related

- [Inspector library](inspector-library.md)
- [CI integration](ci-integration.md) — gate on `--priority` until `--pack` ships.
