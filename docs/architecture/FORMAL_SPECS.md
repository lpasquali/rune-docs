 
# Formal TLA+ Specifications

This section documents the formal TLA+ specifications for critical correctness properties of the RUNE platform.

 
## Job State Machine (`JobStateMachine.tla`)

### What it models

- **Linear Lifecycle**: `queued → running → succeeded | failed`.
- **Idempotency**: `(tenant, idempotency_key)` pairs are unique.
- **No Regression**: Terminal states are final.

### Key Invariants

- `TypeInvariant`: All job records are well-typed.
- `NoRegression`: Terminal jobs stay terminal.
- `IdempotencyInvariant`: No duplicate idempotency-key pairs.

---

 
## Fail-Closed Estimation (`FailClosedEstimation.tla`)

### What it models

- **Confidence Threshold**: 95% (fail-closed threshold).
- **Atomic Transition**: Dropping below 95% confidence transitions the system to `halted`.
- **Operator Recovery**: Recovery to `active` requires explicit operator action.

### Key Invariants

- `FailClosedInvariant`: `confidence < 95 ⇒ systemState = "halted"`.
- `ActiveOnlyWhenSafe`: `systemState = "active" ⇒ confidence ≥ 95`.

---

 
## Running the Specs

Specs can be verified using the [TLA+ Toolbox](https://lamport.azurewebsites.net/tla/toolbox.html) or the standalone TLC jar.

### Run TLC (Command Line)

```bash
java -jar tla2tools.jar -config spec/JobStateMachine.cfg spec/JobStateMachine.tla
java -jar tla2tools.jar -config spec/FailClosedEstimation.cfg spec/FailClosedEstimation.tla
```

### VS Code Integration

Install the [TLA+ extension](https://marketplace.visualstudio.com/items?itemName=alygin.vscode-tlaplus) and use the **"TLA+: Check model with TLC"** command.
