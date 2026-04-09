# Advanced Pipelines & Compliance Views

RUNE exposes two run-scoped inspection surfaces for multi-agent and
compliance-heavy workflows:

| Surface | UI route | Backing API | Primary use |
|---|---|---|---|
| Chain DAG | `/chains/{run_id}` | `GET /v1/chains/{run_id}/state` | Visualize a multi-agent execution graph while it runs |
| Audit artifacts | `/audits/{run_id}` | `GET /v1/audits/{run_id}/artifacts` | Browse and download compliance evidence for a run |

These views are implemented in `rune-ui`, but they are thin shells around
first-class `rune` API endpoints. The API contracts below are the stable
integration points; the UI only renders them.

## Chain DAG

The chain page is a server-rendered HTML shell plus a zero-NPM, vanilla
JavaScript SVG renderer. On first load, `rune-ui` pre-fetches chain state so
the initial HTTP response reflects upstream success vs. unknown-run errors. The
browser then refreshes the graph while the chain is still running.

### What the page shows

- Overall chain status (`pending`, `running`, `success`, `failed`, `skipped`)
- Directed edges between chain steps
- One node per agent step, labeled with `agent_name` when present
- A detail panel with node status, start time, finish time, and error text
- Manual **Refresh** and **Pause/Resume** controls

### State contract

`GET /v1/chains/{run_id}/state` returns a JSON document with this shape:

```json
{
  "run_id": "chain-abc",
  "overall_status": "running",
  "nodes": [
    {
      "id": "draft",
      "agent_name": "holmes",
      "status": "success",
      "started_at": 1712660000.0,
      "finished_at": 1712660020.0,
      "error": null
    },
    {
      "id": "review",
      "agent_name": "consensus",
      "status": "running",
      "started_at": 1712660021.0,
      "finished_at": null,
      "error": null
    }
  ],
  "edges": [
    {"from": "draft", "to": "review"}
  ]
}
```

Important behavior:

- If the run exists but no chain state has been recorded yet, the API returns an
  empty shell with `nodes: []`, `edges: []`, and `overall_status: "pending"`.
- If the run is unknown or belongs to a different tenant, the API returns
  `404`.
- The UI keeps polling only while `overall_status` is `running`.

## Audit Artifact Viewer

The audit page is a static shell that fetches artifact metadata client-side and
renders one card per artifact. Cards are grouped by `kind` and expose both
inline previews and raw downloads.

### Artifact kinds

The current viewer recognizes these artifact kinds:

- `slsa_provenance`
- `sbom`
- `tla_report`
- `sigstore_bundle`
- `rekor_entry`
- `tpm_attestation`

Inline previews are rendered for:

- `slsa_provenance`
- `sbom`
- `tla_report`

Binary or opaque artifacts such as Sigstore, Rekor, and TPM evidence are still
listed, hashed, and downloadable, but they are not expanded inline.

### Metadata contract

`GET /v1/audits/{run_id}/artifacts` returns summary data plus one metadata entry
per artifact:

```json
{
  "run_id": "bench-123",
  "summary": {
    "total_count": 2,
    "kinds_present": ["sbom", "slsa_provenance"]
  },
  "artifacts": [
    {
      "artifact_id": "aid-1",
      "kind": "slsa_provenance",
      "name": "provenance.json",
      "size_bytes": 512,
      "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "created_at": 1712660100.0,
      "download_url": "/v1/audits/bench-123/artifacts/aid-1"
    }
  ]
}
```

The list endpoint intentionally omits raw bytes. Artifact content is retrieved
via `GET /v1/audits/{run_id}/artifacts/{artifact_id}` and streamed with an
attachment filename and content type.

### Operational notes

- An existing run with no audit evidence returns `200` with `artifacts: []`.
- Unknown runs return `404`.
- Audit artifact endpoints are tenant-scoped and require the same API auth as
  the rest of `rune`.

## How To Validate

### Chain graph

1. Start a run that records chain state.
2. Open `/chains/{run_id}` in `rune-ui`.
3. Confirm the SVG renders nodes and edges and that the status badge updates.
4. Click a node and verify the detail panel populates with status/timestamps.

### Audit evidence

1. Start or select a run with recorded audit artifacts.
2. Open `/audits/{run_id}` in `rune-ui`.
3. Confirm the summary badge count matches the returned artifact list.
4. Open inline previews for SLSA, SBOM, or TLA+ artifacts.
5. Download at least one artifact and verify the filename and bytes match the
   API response.

## Related References

- [API Specification](API_SPEC.md)
- [Interfaces](INTERFACES.md)
- [Deployment](../operations/DEPLOYMENT.md)
