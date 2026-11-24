# Agent briefs: "Do LLMs Get More Lost in Bangla?"

These files replace `docs/AGENT_PROMPT.md` as the instructions for coding agents (Claude Code, Codex, Antigravity, ...).

## How to use them

1. Give the agent **`00-context.md` plus one phase brief**. Every brief assumes the agent has read `00-context.md`.
2. The agent works only on that phase, then stops and writes its checkpoint report.
3. A person reads the report and approves (or not) before the next brief is handed out.
4. Facts that later phases need (hashes, endpoints, counts, decisions) go into `STATE.md`. Agents read it at the start and update it at the end. Never rely on chat memory between agents.

## Order

| Brief | What it does | Needs first |
| --- | --- | --- |
| `01-setup.md` | Repo layout, Python env, servers, model client, smoke test | nothing |
| `02-models.md` | Get the models, measure speed and memory, time estimate | 01 |
| `03-reproduce.md` | Rerun the paper's math test (English, Llama + Phi-4) | 02 |
| `04a-dataset.md` | Build the English–Bangla dataset, native-speaker review | 01 (simulator server only) |
| `04b-pilot.md` | Pick the tested models on 50 Bangla problems | 03 passed, 04a frozen |
| `04c-main-runs.md` | All main runs | 04b |
| `04d-analysis.md` | Tables, ranges, plots, summary | 04c |
| `05-extra-tasks.md` | Optional: the other upstream tasks, only if time allows | 03 |

**Start 04a early.** It only needs the simulator server, and the native-speaker review takes days because it waits on people. Run it beside 02 and 03.
