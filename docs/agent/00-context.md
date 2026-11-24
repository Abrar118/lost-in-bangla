# 00. Shared context (read this before any phase brief)

## The project

A 6-person student group (MIST, CSE 6701 Advanced AI). Research question: **does splitting the same math problem across chat turns hurt accuracy more in Bangla than in English?**

- **Base paper:** Laban et al., "LLMs Get Lost in Multi-Turn Conversation" (ICLR 2026). PDF: `docs/original-paper/`.
- **Base code:** <https://github.com/microsoft/lost_in_conversation> (MIT licence). Commit seen on 2026-11-24: `c865793fe34a929d316119b0451d01bd9183bcfd`. Check it again when copying.
- **Our proposal:** `docs/proposal/proposal.tex`.
- **Data for the extension:** MGSM-Rev2 (Peter et al., "Mind the Gap... or Not?", GEM 2026, arXiv 2511.05162). 250 GSM8K problems in 11 languages, CC BY-SA 4.0.

## Settings (same names as the paper)

| Setting | What the tested model sees |
| --- | --- |
| FULL | The original problem in one message |
| CONCAT | All pieces ("shards") joined in one message |
| SHARDED | One shard per turn. Shard 1 always comes first; the simulated user picks which shard comes next. |
| SNOWBALL | Like SHARDED, but each turn repeats all earlier shards |

**Main result:** Δ = (CONCAT − SHARDED) in Bangla − (CONCAT − SHARDED) in English, in accuracy points, with a 95% range.

**Second result:** the *share* of the score lost, (CONCAT − SHARDED) / CONCAT, per language. Reason: a weak score cannot fall far, so counting points alone can make the weaker language look "less lost" than it is.

## Hard rules

1. **No paid API calls, ever** (OpenAI, Azure, Anthropic, Google, ...). If any code path would call one, disable it and say so in the report.
2. **Serving:** `llama-server` from llama.cpp, behind its OpenAI-compatible endpoint. No Ollama.
3. **Upstream code:** copy it into `upstream/` and record the commit hash. **Editing upstream files is allowed.** List every edit, with the reason, in `upstream/OUR_CHANGES.md`.
4. **Ask a person before you:**
   - change or install anything **outside this repo** (system packages, `G:\Agents\`, firewall rules, `llm-models.ini`, Homebrew on the Mac, copying model files, ...)
   - accept any licence or terms (for example the Llama licence on Hugging Face)
   - download anything over 20 GB
   - delete data
   - change the research design
5. **One config file**, `config.yaml`, holds:
   - model files and quantisation
   - endpoints and seeds
   - sampling settings and token limits
   - number of runs
   - file paths

   No hard-coded copies elsewhere.
6. **Never invent numbers.** Every number in a report must come from a file the code wrote. If something did not run, say so.
7. **Log everything:** one JSONL line per conversation (fields below).
8. **Keep it simple.** Small scripts, no frameworks. Use the installed Python and a plain `venv`. **Do not install `uv`.** Pin package versions in `requirements.txt`.
9. **Platforms:** Windows and macOS only. **No Linux or WSL set-up.** Every script must run on both. Prefer Python scripts over `.sh` / `.bat`.

## Writing rule for anything people read

This covers reports, `README.md`, `results/summary.md`, review sheets and their instructions, and checkpoint reports.

- Plain, simple English. Short sentences.
- **No jargon.** For example, write "95% range (we reshuffled the problems 10,000 times)", not "bootstrap CI". Write "the share of the score lost", not "relative degradation".
- If a technical word can't be avoided, explain it in one short line the first time.
- Mark every guess as a guess.

Code comments and agent-to-agent notes may be technical.

## Machines (checked 2026-11-24 on the desktop; check again)

| Machine | Facts | Role |
| --- | --- | --- |
| Windows desktop | RTX 5060 Ti 16 GB, 32 GB RAM, Windows 11, Python 3.12.10. llama.cpp CUDA build at `G:\Agents\llama-cpp\llama-server.exe` (not on PATH). | **Simulator + checker** (Qwen), on the local network |
| MacBook Pro | M5 Pro, 24 GB unified memory (not yet checked) | **Tested models** (llama.cpp with Metal) and the run scripts |
| Second PC | RTX 3070 8 GB, rarely available | Spare only |

- **Simulator file:** `G:/Agents/models/Qwen3.8-27B-GSQ-RCO-IQ3_S.gguf` (11.8 GB). It should fit fully on the 16 GB GPU; measure this.
- **Gemma 4 12B:** `G:/Code/MSc/abrar-thesis/models/gemma4/gemma-4-12B-it-Q4_K_M.gguf` (7.7 GB).
- **Do not use or edit** the user's `G:\Agents\llm.bat` / `llm-models.ini` router. Our own serve script starts `llama-server` with settings from `config.yaml`.

## Fixed design decisions (approved 2026-11-24)

**Models**
- **Simulator:** Qwen3.8-27B IQ3_S with **thinking off**. It plays the user, decides whether a reply is an answer attempt, and pulls out the answer. Every call that went to GPT-4o / GPT-4o-mini upstream goes to it.
- **Tested models:** Llama-3.1-8B-Instruct, Phi-4 (14B), Gemma 4 12B, gpt-oss-20b. Default quantisation is Q4_K_M; gpt-oss uses its native MXFP4. The same file is used for English and Bangla.

**Sampling and limits**
- **Sampling:** match the paper. Temperature 1.0, top_p 1.0, top_k 0, min_p 0, for every tested model in both languages.
- **Simulator sampling:** keep upstream's settings and record them.
- **Seeds:** each request's seed comes from (problem, setting, language, run) and is logged.
- **Token limit:** upstream caps replies at 1000 tokens. Bangla needs more tokens per word, so this cap would hurt Bangla more. Put the limit in `config.yaml`, set it high enough, log `finish_reason`, and report the cut-off rate per language.
- **Thinking text** (gpt-oss, and Gemma 4 if it produces any) is kept out of the visible conversation but logged. gpt-oss's reasoning level goes in `config.yaml`.

**Answer checking**
- **Phase 3:** upstream's checker, unchanged, so we stay comparable with the paper.
- **Phase 4:** our checker (rules below). Log both scores in Phase 4.
- Our checker takes the final number and:
  - turns Bangla digits ০–৯ into 0–9
  - removes thousands separators
  - removes units
  - compares as numbers; correct means exactly equal
- **End of a conversation:** on a correct answer, or when the shards run out (upstream rule).

**Phase 4 conversations**
- **Language:** everything the tested model reads is in the conversation's language. That includes upstream's short instruction (system) message, translated and checked by native speakers.
- **Simulator prompts:** its private instructions stay in English.
- **Shard wording:** in Phase 4 the simulated user still **picks** the next shard, but pastes its text **word for word** in both languages; it does not reword it. Phase 3 keeps upstream's rewording, to match the paper.
- **FULL text:** Bangla FULL uses the human-translated MGSM-Rev2 Bangla text; English FULL uses the MGSM-Rev2 English text. CONCAT and SHARDED use our shards. A big Bangla FULL − CONCAT gap is a warning that the shard translations may be poor.

**Runs and checks**
- **Runs:** 5 per setting. If the Phase 2 time estimate leaves room, use 10 for SHARDED, since "best vs worst run" numbers are shaky with 5. The team decides at Checkpoint 2.
- **Gate after Phase 3:** SHARDED must be at least **10 points below FULL for both models**. If not, stop and report.
- **Scope:** math first. Other upstream tasks only if time allows (`05-extra-tasks.md`).
- **Licence:** our released dataset is CC BY-SA 4.0, because MGSM-Rev2 requires it.

## Log format (one JSONL line per conversation)

`conversation_id, phase, task, setting, language, problem_id, run_id, tested_model, tested_quant, tested_file_sha256, simulator_model, simulator_quant, seed, sampling (dict), max_tokens, shard_order (list), turns (list of {role, text, reasoning_text?, finish_reason?, tokens}), extracted_answer, correct_upstream, correct_ours, simulator_calls (list of {purpose, prompt, output}), started_at, ended_at, error`

- Append one line as each conversation finishes.
- A rerun skips conversations that are already logged, so a crash loses nothing.

## Known facts about the upstream code (read 2026-11-24)

- `model_openai.py`:
  - needs `OPENAI_API_KEY` / Azure keys
  - its cost calculator **raises an error** for any model name it doesn't know
- `user_agent.py` defaults to `gpt-4o`. `run_simulations.py` defaults every model to `gpt-4o-mini`.
- The real runner is `run_simulations.py`; its README wrongly says `run_experiments.py`.
- Imports are flat and paths relative (`prompts/...`, `data/...`), so scripts must run with `upstream/` as the working folder.
- `simulator_sharded.py` sets `max_tokens = 1000` unless the model name contains `o1`, `o3` or `deepseek-r1`.
- `tasks/math/task_math.py`:
  - its checker compares **strings** after stripping `,` and `$`, so "18.00" ≠ "18"
  - it expects the GSM8K answer format `... #### 18`
  - `get_dataset_file()` returns `data/sharded_math.json`, a file that doesn't exist upstream. Check how `run_simulations.py` actually loads data.
- `run_simulations.py` already skips finished runs by counting its own logs. Reuse that idea.
- Upstream's README says the **code** task doesn't work on Windows, and the **database** task needs a roughly 5 GB Spider download.

## Checkpoint report (every phase)

Plain English, following the writing rule:

1. What was done
2. What was found, with numbers from files (give the file paths)
3. What failed or looks wrong
4. What's next

Then **stop and wait for approval.**
