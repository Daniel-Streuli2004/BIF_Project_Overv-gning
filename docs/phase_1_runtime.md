# Phase 1 Runtime Guide

This document describes exactly what was implemented for Phase 1 and how you validate it.

## 1. What Was Created

- Notebook created:
  - `notebooks/agent_people.ipynb`
- Documentation updated:
  - `docs/exercises.md`
  - `docs/phase_1_runtime.md`
- Library modules added in `src/simulated_city/`:
  - None
- Configuration changes in `config.yaml`:
  - None

## 2. How to Run

### Workflow A: Run the Phase 1 people agent notebook

1. Start JupyterLab:
   - `python -m jupyterlab`
2. Open `notebooks/agent_people.ipynb`.
3. Run cells 1-8 in order.
4. Observe output in each code cell:
   - Cell 2 confirms config loading.
   - Cell 3 confirms data model setup.
   - Cell 4 prints entry/exit counts and seed.
   - Cell 5 confirms movement helpers.
   - Cell 6 confirms 50 people initialized as white.
   - Cell 7 runs the simulation and prints final summary + sample records.

### Workflow B: Verify project checks still pass

1. Run `python scripts/verify_setup.py`
2. Run `python scripts/validate_structure.py`
3. Run `python -m pytest`

## 3. Expected Output

### Notebook outputs (exact/pattern checks)

- **Cell 2 (imports + config):**
  - Exact prefix line: `Loaded config. MQTT base topic: simulated-city`
  - Exact prefix line: `Simulation section present: `
  - Success means config was loaded correctly.

- **Cell 3 (data model):**
  - Exact line: `Defined PersonState dataclass for local simulation state.`

- **Cell 4 (constants + targets):**
  - Exact line: `Entries configured: 4`
  - Exact line: `Exit waypoints configured: 4`
  - Exact line: `Using random seed: 42`

- **Cell 5 (helpers):**
  - Exact line: `Movement helper functions are ready.`

- **Cell 6 (initialization):**
  - Exact line: `Initialized 50 people.`
  - Exact line: `Initial white count: 50`

- **Cell 7 (simulation run):**
  - Exact line: `Phase 1 simulation complete.`
  - Exact line: `Final counts -> white=0, green=39, red=11, exited=3, inside_count=39`
  - Exact prefix line: `Sample records (first 3 people):`
  - Expected first sample record:
    - `{'person_id': 'p001', 'name': 'Alex', 'state': 'inside', 'color': 'green', 'target_entry_id': 'E1'}`

### If output is different

- Different final counts usually mean one of:
  - cell order changed,
  - constants were modified,
  - random seed is not `42`.
- If `Simulation section present: True`, configured simulation values may override defaults and change behavior.

### Success criteria

- Notebook runs from top to bottom with no errors.
- 50 people start white.
- At the end, no one remains white.
- Green and red transitions happen only at entry attempt.
- Denied people move to exiting/exited and do not re-attempt.

## 4. MQTT Topics (if applicable)

Phase 1 uses no MQTT.

- Topics published: none
- Topics subscribed: none
- Message schemas: none

## 5. Debugging Guidance

### Enable more visibility

- Re-run Cell 7 and add temporary `print()` statements inside state transitions if needed.
- Inspect `simulation_log[-5:]` in a new cell to view recent tick summaries.

### Common errors and fixes

- **`ModuleNotFoundError: simulated_city`**
  - Run from workspace root and ensure editable install is done:
  - `pip install -e ".[dev,notebooks]"`
- **Config not found**
  - Ensure notebook is opened from this repository and `config.yaml` exists at root.
- **Unexpected final counts**
  - Verify constants in Cell 4 and seed value (`42`).
  - Run all cells from a clean kernel restart.

### MQTT flow checks

- Not applicable in Phase 1.

## 6. Verification Commands

```bash
python scripts/verify_setup.py
python scripts/validate_structure.py
python -m pytest
```
