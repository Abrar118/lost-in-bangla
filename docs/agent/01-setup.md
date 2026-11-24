# 01. Set up the repository

Read `00-context.md` and `STATE.md` first.

## Tasks

1. **Layout**

   ```
   upstream/   copy of the base code (commit hash in STATE.md and upstream/UPSTREAM_COMMIT)
   src/        our code
   data/
   configs/    config.yaml lives here
   scripts/
   results/    git-ignored, except summaries
   notebooks/
   ```

2. **Python:** create a `venv` with the installed Python (3.12 on Windows; check the Mac). Install upstream `requirements.txt` plus our extras, with pinned versions. No `uv`.

3. **Serve script:** `scripts/serve.py <model-key>` reads `configs/config.yaml` and starts `llama-server` for that model.
   - **Windows:** use `G:\Agents\llama-cpp\llama-server.exe`; the path goes in the config.
   - **Mac:** check whether llama.cpp is installed. If it isn't, **ask** before building or installing it.
   - **Simulator settings:** thinking off, a context size that fits, and the server listening on the local network.
   - **Firewall:** opening the Windows firewall is outside the repo, so **ask** first.

4. **Model client:** `src/model_local.py`, an OpenAI-compatible client for our `llama-server` URLs. Wire it in, editing upstream if needed and listing the edits in `upstream/OUR_CHANGES.md`:
   - tested-model calls go to the tested-model server
   - simulated user, answer-type check and answer extraction go to the simulator server
   - every `gpt-4o` / `gpt-4o-mini` default goes to the simulator
   - the cost calculator returns 0 instead of raising
   - thinking text is removed from the visible reply and logged
   - sampling, seed and token limit come from `config.yaml`
   - search the whole `upstream/` folder for `openai`, `azure`, `anthropic`, `google` and `api_key`, and report every hit

5. **Logger:** write the JSONL format from `00-context.md`, and skip conversations that are already logged.

6. **Smoke test:** upstream math task, **3 problems × FULL and SHARDED × 1 run**, using **Gemma 4 12B** as the tested model. It's already on disk; Llama comes in Phase 2.
   - **Preferred:** Gemma on the Mac, Qwen on Windows. Copying the Gemma file to the Mac is outside the repo, so **ask** first.
   - **Fallback:** both on Windows, with part of the load moved to the CPU. Slow, but fine for 3 problems.

7. **Viewer:** `scripts/show_conversation.py <log> <conversation_id>` prints one conversation in readable form.

## Checkpoint 1 report
- the layout tree and the upstream commit
- the machines found: GPU, memory, OS and Python, on each machine
- a placement plan with measured memory use
- the smoke-test log path, plus one full SHARDED conversation printed in readable form
- every place upstream pointed to a paid API, and how it was turned off
- the contents of `upstream/OUR_CHANGES.md`
