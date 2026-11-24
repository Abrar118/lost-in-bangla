# Our changes to the upstream code

Base: https://github.com/microsoft/lost_in_conversation at commit `c865793fe34a929d316119b0451d01bd9183bcfd` (MIT licence).
We copied everything except the `.git` folder. Any file not listed here is unchanged.

| File | Change | Why |
| --- | --- | --- |
| `model_openai.py` | Whole file replaced by a 3-line link to `src/model_local.py`. | The original called the paid OpenAI / Azure API and needed keys. Keeping the file name means no other file needs a new import. |
| `user_agent.py` | Added `purpose="user_turn"` to its one `generate_json` call. | Our logger records what each simulator call was for. No change in behaviour. |
| `system_agent.py` | Added `purpose="turn_check"` and `purpose="answer_extraction"` to its two `generate_json` calls. | Same as above. |
| `simulator_full.py` | Added `self.trace = trace` after the trace is built. | The sharded simulator already keeps its trace; the full one did not. Our runner needs it to log the conversation. |

## What `src/model_local.py` does differently from the old `model_openai.py`

- Calls our own `llama-server` endpoints (`configs/config.yaml`). No API key, no paid service.
- `generate_json` (simulated user, turn check, answer extraction) always goes to the **simulator** server. The `model` name passed in is ignored, so every `gpt-4o` / `gpt-4o-mini` default ends up there.
- `generate` (the tested model) needs a tested-model key from the config. Any other name, such as a leftover `gpt-4o-mini`, raises an error instead of going to the wrong server.
- Temperature, top_p, top_k, min_p, token limit, timeout and seed for the tested model come from the config. The caller's `max_tokens` and `timeout` are ignored. The simulator keeps the caller's temperature (upstream sets it per call).
- The cost calculator is gone; `total_usd` is always 0 (it used to raise an error for unknown model names).
- Thinking text is split from the reply: the server's `reasoning_content` field, or a `<think>...</think>` block. The visible reply never contains it. It is stored in the log.
- Every call is recorded (prompt, output, thinking, finish reason, tokens, seed) for the log.

## Files we did not touch but do not use

`run_simulations.py`, `simulator_recap.py`, `simulator_snowball.py` and `utils_log.py` are unchanged. We run conversations with `src/run_conversations.py` instead, which logs in our own format.
`run_simulations.py` and the two simulators' `__main__` blocks still default to `gpt-4o-mini` for the tested model; with our client that now raises an error, so they cannot be run by accident.

## Paid-API search

Searched all of `upstream/` (after our edits) for `openai`, `azure`, `anthropic`, `google`, `api_key`. Results are in the Phase 1 report: `docs/agent/reports/01-setup.md`.
