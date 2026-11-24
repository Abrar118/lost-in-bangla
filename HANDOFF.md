# Handoff: Mac Claude to Windows Claude

Written 2026-11-24 on the Mac. Read this first, then `docs/agent/00-context.md`, `docs/agent/STATE.md` and `docs/agent/reports/01-setup.md`. The hard rules in `00-context.md` still apply (no paid APIs, ask a person before anything outside the repo, never invent numbers, plain English in anything people read).

## Where things stand

- **Phase 1 code is done and merged to `main`.** Layout, upstream copy (commit `c865793`), local model client, runner, logger, viewer, serve script, one config file.
- **Phase 1 is not signed off.** The real smoke test has not run, because the Qwen simulator lives on this Windows desktop. That is your first job.
- Nothing from Phase 2 onwards has been started.
- The Mac dry run (6 conversations, stand-in simulator Qwen3.5-9B) passed with no errors. Its log is in `results/logs/` on the Mac only (git-ignored, not in the repo). Do not treat it as a result.

## Your first tasks, in order

1. `git pull` on `main`. Make a venv: `py -3.12 -m venv .venv`, then `.venv\Scripts\python -m pip install -r requirements.txt`. The pins were made on macOS; if a package does not install on Windows, fix the pin and say so.
2. Check the installed llama.cpp (`G:\Agents\llama-cpp\llama-server.exe --version`). Record the version in `STATE.md`. The Mac build is 12359 (`b1b770d90`). `scripts/serve.py` passes `--alias`, `--jinja`, `-np`, `-c`, `-ngl` and `--cache-ram 0`. If this older/newer build rejects one, change `extra_args` or `serve.py`, and note it in `upstream/OUR_CHANGES.md`-style notes in the report.
3. `python scripts/serve.py simulator --dry-run` to see the command, then without `--dry-run`. Confirm Qwen3.8-27B IQ3_S fits the 16 GB GPU at context 16,384 (a guess). Lower `ctx_size` in `configs/config.yaml` if not. **Record measured GPU memory.**
4. **Firewall: ask the person first** (rule 4 in `00-context.md`). The proposed rule: allow TCP 8081 only from the Mac's address, private network profile only. The simulator listens on `0.0.0.0` and llama-server has no login, so this rule is the only access control. Do not open it wider.
5. Set `endpoints.simulator` in `configs/config.yaml` to the address the tested-model machine uses (still `127.0.0.1` now). Ask the person where the tested model and the runner will run (see open question A).
6. **Check thinking is off on the simulator.** Every request sends `chat_template_kwargs: {enable_thinking: false}`. After the first calls, `reasoning_text` must be empty in every `simulator_calls` entry. This was only verified on Qwen3.5-9B. If Qwen3.8-27B still thinks, find the right switch (a server flag such as `--reasoning off`, or another template key).
7. Run the smoke test: `python src/run_conversations.py --phase smoke --model gemma4-12b --problems 3 --settings full sharded --runs 1`. Print one SHARDED conversation with `python scripts/show_conversation.py results/logs/smoke_gemma4-12b.jsonl <id> --calls`. Add the log path and that conversation to `docs/agent/reports/01-setup.md`, update `STATE.md`, then stop for approval.
8. Also fill in the simulator file's SHA256 (`certutil -hashfile <file> SHA256`) and the Windows Gemma copy's hash in `STATE.md` and `config.yaml`.

## Open questions for the person (do not decide these yourself)

- **A. Where does each piece run?** The plan in `00-context.md` is Qwen on Windows, tested models on the Mac. The person has now said long runs should happen on Windows. Qwen3.8-27B IQ3_S (11.8 GB) and Gemma 4 12B (7.7 GB) will not both fit the 16 GB GPU, so one of them would run partly on the CPU and be slow. Options: (1) keep the split, with the runner on either machine and the tested model reachable over the network; (2) everything on Windows with CPU offload. If the Mac serves the tested model to Windows, it must listen on the network, which needs its own access rule. Ask before changing anything.
- **B. Gemma thinking on or off.** Not decided. Gemma 4 12B thinks by default (the server returns it as `reasoning_content`, which we keep out of the chat and log). `chat_template_kwargs: {enable_thinking: false}` switches it off (tested on the Mac: 561 tokens became 155 on one problem; the other key I tried, `thinking`, did nothing). It changes a tested model's behaviour, so it needs team approval. The person asked for a comparison: Gemma FULL, English, 50 problems, thinking on versus off, same problems. Estimate: about 30 to 40 minutes. To run it, add a second entry under `tested_models` using the same file with `request_extra: {chat_template_kwargs: {enable_thinking: false}}` (for example `gemma4-12b-nothink`), then run both with `--settings full`. With 50 problems the 95% range is about ±10 points, so only a big gap will show. Run it only after the person confirms, and with the real simulator.
- **C. Phase 2 can start without the smoke test passing**, but its time estimate needs both the real simulator speed and answer B. Model downloads need a person to accept the Llama licence and approve any copy of files (rules in `02-models.md`).

## Things that will bite you

- **Memory:** llama-server keeps a RAM prompt cache, default 8 GiB, that grows to the cap. On the Mac it pushed one server to about 20 GB. `--cache-ram 0` is set in the config for both servers and fixed it (about 13.3 GB total for Gemma on the Mac). Do not measure memory with `ps` RSS on a Mac; it misses GPU memory. On Windows, measure GPU memory with `nvidia-smi`.
- **Run from the right folder.** Upstream code uses relative paths (`prompts/...`, `data/...`). `src/run_conversations.py` changes into `upstream/` itself, so run it from the repo root.
- **Routing:** `generate_json` calls (simulated user, turn check, answer extraction) always go to the simulator server. `generate` (the tested model) needs a key from `tested_models` in the config, otherwise it raises an error. Model names like `gpt-4o-mini` are ignored or rejected, never sent anywhere.
- **Token limit:** the tested-model reply limit is 4,096 (a guess; includes thinking text). The simulator reply limit is 1,024. Phase 2 must check the cut-off rate, especially on Bangla.
- **Simulator sampling:** upstream sets only the temperature per call (0.0 for the checker and extractor, 1.0 for the user). Everything else is llama-server's default (top_k 40, top_p 0.95, min_p 0.05), which differs from OpenAI's. It is logged; do not hide it.
- **Reruns skip finished conversations** (key: problem, setting, language, run, model, for lines with no error). Conversations that errored are retried and appended again, so analysis must take the last good line.
- **`correct_ours` is `null` on purpose** until Phase 4 (our checker). `SNOWBALL` is not wired into the runner yet; it is not needed until Phase 4.
- **`results/` is git-ignored.** Logs do not travel through git. Copy what the other machine needs.
- Upstream prints some harmless `SyntaxWarning` lines about regex strings when it starts. Ignore them.
- `upstream/tasks/actions/eval_bfcl.py` calls `eval()` on model output (lines 145 and 156). Unchanged upstream code, used only by the optional `actions` task. If Phase 5 runs it, patch it first (use `ast.literal_eval`). Math never touches it.
- The assumptions the person already reviewed and approved: Gemma file used in place (no copy); 4,096 and 1,024 token limits as placeholders; JSON calls always go to the simulator; `correct_ours` null until Phase 4.

## Map of the code

| File | What it does |
| --- | --- |
| `configs/config.yaml` | The only config: model files, servers, endpoints, sampling, token limits, seeds, paths |
| `scripts/serve.py <key>` | Starts llama-server for `simulator` or a tested-model key (`--dry-run` prints the command) |
| `src/model_local.py` | Local client replacing upstream's paid-API client; routing, seeds, thinking split, call recording |
| `src/run_conversations.py` | Runs FULL / CONCAT / SHARDED with upstream's simulators and writes our JSONL log |
| `src/conv_log.py` | Append-only JSONL writer and the "already done" check |
| `scripts/show_conversation.py` | Prints one logged conversation (`--calls` adds the simulator's calls) |
| `upstream/OUR_CHANGES.md` | Every edit to Microsoft's code, with reasons |
| `docs/agent/reports/01-setup.md` | Checkpoint 1 report (what was found, what failed) |

## When you finish

Update `STATE.md` (endpoints, hashes, measured memory, decisions), extend the report, commit, and stop and wait for approval before Phase 2. Delete this file once its contents are in `STATE.md` and the reports.
