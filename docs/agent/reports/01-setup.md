# Checkpoint 1: set-up report

Status: **code is done and tested on the Mac. The real smoke test still needs the Windows simulator.** Please read section 3.

## 1. What was done

- Copied the upstream code into `upstream/` at commit `c865793fe34a929d316119b0451d01bd9183bcfd` (same as the commit seen on 2026-11-24; checked again with `git ls-remote`). The hash is in `upstream/UPSTREAM_COMMIT`.
- Made a Python 3.12.10 `venv` (`.venv/`) and pinned all packages in `requirements.txt`. No `uv`.
- Wrote `configs/config.yaml`: the one place for model files, servers, sampling, token limit, seeds and paths.
- Wrote `scripts/serve.py <simulator|model-key>`: starts `llama-server` using the config. Works on Windows and Mac (it picks the right entry for the machine).
- Wrote `src/model_local.py`: the client for our own servers. It replaces the paid-API client (details in `upstream/OUR_CHANGES.md`).
- Wrote the logger (`src/conv_log.py`) and a runner (`src/run_conversations.py`). One JSONL line per conversation, in the format from `00-context.md`. A rerun skips conversations already logged.
- Wrote `scripts/show_conversation.py`: prints one conversation in readable form.

### Layout

```
upstream/        copy of the base code + UPSTREAM_COMMIT + OUR_CHANGES.md
src/             config.py, model_local.py, conv_log.py, run_conversations.py
configs/         config.yaml
scripts/         serve.py, show_conversation.py
data/  notebooks/  (empty for now)
results/         git-ignored (logs are written to results/logs/)
requirements.txt
```

## 2. What was found

### Machines

| | Mac (checked by me today) | Windows desktop |
| --- | --- | --- |
| Chip / GPU | Apple M5 Pro, 16 GPU cores, Metal 4 | RTX 5060 Ti 16 GB (from `00-context.md`; **I did not check this**) |
| Memory | 24 GiB (`sysctl hw.memsize` = 25,769,803,776 bytes) | 32 GB (from `00-context.md`) |
| OS | macOS (Darwin 27.2.0) | Windows 11 (from `00-context.md`) |
| Python | 3.12.10 | 3.12.10 (from `00-context.md`) |
| llama.cpp | Homebrew, `/opt/homebrew/bin/llama-server`, build 12359 (commit b1b770d90) | `G:\Agents\llama-cpp\llama-server.exe`, version **not checked** |

### Placement plan and memory

- **Mac: tested models.** Gemma 4 12B Q4_K_M, started with `serve.py gemma4-12b` (context 16,384, all layers on the GPU). Measured memory (corrected after you flagged 22 GB): my first figure (8.2 GB from `ps`) missed GPU memory and was wrong. With the real measure (`vm_stat` wired memory plus `footprint`): loading adds about **8.6 GB wired** (model, KV cache, compute buffers), plus about 0.8 GB process memory. Idle total is about **9.4 GB**. llama-server also keeps a **RAM prompt cache that defaults to 8 GiB**; in a test with six different long prompts the process grew from 0.8 GB to 6.6 GB, so the total heads toward ~20 GB or more. That is the 22 GB. Fixed with `--cache-ram 0` in `configs/config.yaml` (both servers). After the fix the same test stayed at 1.56 GB process + 11.7 GB wired (**about 13.3 GB total**) and did not grow. This only changes memory and speed, not answers.
- **Windows: simulator.** Qwen3.8-27B IQ3_S is 11.8 GB on disk and should fit the 16 GB GPU with a 16,384 context. **I have not measured this**; I cannot reach that machine. The context size in the config is a guess.
- The Gemma file is read in place from `/Users/orion-abrar/Code/masters/Thesis/models/gemma4/`. Nothing was copied. Its SHA256 is in the config (`3962624d...1671509`, size 7,662,533,088 bytes). The Windows copy's hash has not been checked.

### Dry run (not the real smoke test)

I ran the plumbing end to end with **Qwen3.5-9B Q4_K_M on the Mac as a stand-in simulator** (the real Qwen3.8-27B is only on Windows). Gemma 4 12B was the tested model.

- Log: `results/logs/dryrun-standin_gemma4-12b.jsonl` (git-ignored).
- 3 math problems (picked with a fixed seed) × FULL and SHARDED × 1 run = 6 conversations. All 6 finished, none had an error, every reply ended with `finish_reason = stop`.
- Upstream checker marked 5 of 6 correct. This says nothing about accuracy (3 problems, a stand-in simulator).
- Longest single reply: 2,533 tokens (thinking included). The 4,096 limit was never hit.
- It took about 6 minutes (`started_at` / `ended_at` in the log). Gemma wrote about 30 tokens per second.
- Running the same command again said "0 conversations to run (6 already logged)", so the skip works.
- One full SHARDED conversation, in readable form: `docs/agent/reports/01-setup-example-conversation.txt`. The log records `simulator_model: standin`, so this run cannot be mistaken for the real one.

### Every place upstream pointed to a paid API

All of these are now cut off. No key is needed and none is read.

- `model_openai.py`: imported `openai` / `AzureOpenAI`, needed `OPENAI_API_KEY` or the Azure keys. **Replaced** by a link to `src/model_local.py`.
- Every other file only imports `generate` / `generate_json` from `model_openai`, so they now use our client: `user_agent.py`, `system_agent.py`, `simulator_full.py`, `simulator_sharded.py`, `simulator_recap.py`, `simulator_snowball.py`, `tasks/summary/eval_summhay.py`.
- `gpt-4o` / `gpt-4o-mini` names remain as defaults in `user_agent.py`, `run_simulations.py`, the simulators' `__main__` blocks, `tasks/actions/task_actions.py` and `tasks/summary/task_summary.py`. For the simulated user, turn check and answer extraction the name is ignored and the call goes to the simulator. For the tested model, such a name now raises an error, so nothing can reach the wrong server by accident.
- `utils.py` has an unused `load_env_vars` for a `.env` file. Nothing calls it.
- Other hits for "google" / "openai" are only comments and prompt text (for example "like a search engine like Google"). Search command: `rg -i 'openai|azure|anthropic|google|api_key'` over `upstream/`.
- Upstream's README mentions API keys. We did not change the README.

### Contents of `upstream/OUR_CHANGES.md`

See that file. In short: `model_openai.py` replaced; three one-line additions (`purpose=...` labels in `user_agent.py` and `system_agent.py`, and `self.trace = trace` in `simulator_full.py`).

## 3. What failed or looks wrong

1. **The real smoke test is not done.** It needs the Qwen simulator on the Windows desktop. I cannot start it, and opening the Windows firewall is outside the repo, so it needs a person. Steps:
   1. On Windows: pull the repo, make a venv (`py -3.12 -m venv .venv`), `pip install -r requirements.txt`.
   2. Run `python scripts/serve.py simulator`. Check it starts and that the 11.8 GB model fits (lower `ctx_size` in the config if not).
   3. **Allow the port (8081) through the Windows firewall for the local network. Please approve this.**
   4. Put the desktop's address into `endpoints.simulator` in `configs/config.yaml` (it still says `127.0.0.1`).
   5. On the Mac: `python scripts/serve.py gemma4-12b`, then `python src/run_conversations.py --phase smoke --model gemma4-12b --problems 3 --settings full sharded --runs 1`.
2. **Gemma 4 12B thinks by default.** The server returns its thinking text separately, so even "17 × 3" used 93 tokens. We keep the thinking out of the chat and log it (`reasoning_text`). It counts against the 4,096 limit and makes runs slower. Decision for the team: leave it on (matches "kept out of the conversation but logged") or turn it off for Gemma via `request_extra` in the config. I left it on.
3. **Thinking-off for the simulator is only checked on the stand-in.** The request carries `chat_template_kwargs: {enable_thinking: false}`. This worked on Qwen3.5-9B (no thinking text came back). Qwen3.8-27B's chat template may differ. After the real smoke test, check that `reasoning_text` is empty in `simulator_calls`.
4. **Simulator sampling is llama-server's default** (top_k 40, top_p 0.95, min_p 0.05) apart from the temperature that upstream sets per call (0.0 for the checker and extractor, 1.0 for the simulated user). Upstream's OpenAI calls used the OpenAI defaults (top_p 1.0). I could not make these identical; this is a small difference, and it is logged.
5. **Placeholders that are guesses:** reply limit 4,096 tokens (Phase 2 should check the cut-off rate), simulator reply safety limit 1,024 tokens, simulator context 16,384.
6. `correct_ours` is `null` in every log line. Our checker comes in Phase 4 (as agreed).
7. Upstream prints some harmless `SyntaxWarning` lines about regex strings in its database task when it starts. We left them.
8. The upstream `run_simulations.py` is not used. Our runner logs in our own format and supports FULL, CONCAT and SHARDED. **SNOWBALL is not wired in yet** (upstream's snowball simulator has a different set-up); it is not needed until Phase 4.
9. The five assumptions you reviewed (Gemma file used in place, 4,096-token limit, 1,024-token simulator limit, call routing, `correct_ours` null) are in the assumption log.

## 4. What's next

- Run the real smoke test (section 3, item 1) and add its log path and conversation to this report.
- After that is approved: Phase 2 (`02-models.md`), and Phase 4a can start in parallel.
- Nothing is committed yet. Say when you want a commit.
