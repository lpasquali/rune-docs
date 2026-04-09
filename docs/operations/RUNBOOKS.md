 
# RUNBOOKS

Incident response checklists for RUNE.

 
## Common Incident: Vast.ai Instance Stuck in Creating

### Symptom

- CLI or API job hangs in `creating` state for more than 5 minutes.
- Vast.ai dashboard shows instance as `starting` or `errored`.

### Resolution

1.  **Check Vast.ai API Key**: Ensure `VAST_API_KEY` is correct and has funds.
2.  **Manual Termination**: If the instance is in a bad state, use the Vast.ai CLI or dashboard to terminate it to avoid costs.
3.  **Adjust Constraints**: If no offers match, try relaxing `--vastai-min-dph` or `--vastai-reliability`.

 
## Common Incident: Ollama Model Pull Failure

### Symptom

- Workflow fails during `pull_model` phase with connection error.

### Resolution

1.  **Check Ollama Server Connectivity**: Verify `RUNE_OLLAMA_URL` is reachable from the RUNE runner.
2.  **Disk Space**: Ensure the Ollama host has enough disk space for the requested model.
3.  **Model Name**: Double-check the model name (e.g., `llama3.1:8b` vs. `llama3.1`).

 
## Common Incident: Job Store Lock (SQLite)

### Symptom

- `sqlite3.OperationalError: database is locked` in logs.

### Resolution

1.  **Concurrency Check**: Ensure multiple writers aren't trying to access the same `jobs.db` simultaneously without proper locking.
2.  **K8s Volume Mount**: If in K8s, verify the PersistentVolume claim is `ReadWriteOnce` and not mounted by multiple pods.
3.  **Restart**: Restarting the `rune-api` pod may resolve transient locks.

This incident class is specific to the current SQLite-backed deployment model.
For the planned external database direction, see
[DATABASE.md](DATABASE.md) and [DATABASE_HA.md](DATABASE_HA.md).

 
## Incident Response

- Report system-wide outages or security issues to **[luca@bucaniere.us]**.
- Check `S3` sink for evidence of job failure results.
