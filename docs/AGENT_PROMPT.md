# Prompt: "Do LLMs Get More Lost in Bangla?" — implementation

You are helping a 6-person student group (MIST, CSE 6701 Advanced AI) implement a research project. Work in 4 phases. **Stop at the end of each phase**, show the checkpoint report, and wait for approval before starting the next phase.

## 1. What the project is

**Base paper:** Laban et al., "LLMs Get Lost in Multi-Turn Conversation" (ICLR 2026).

- Code: <https://github.com/microsoft/lost_in_conversation> (MIT licence).
- The paper takes a task, cuts it into small pieces ("shards"), and has a simulated user reveal one piece per turn.
- Models score much lower this way than when they get the whole task in one message.

**Our study** asks one question: does splitting the same math problem across turns hurt accuracy **more in Bangla than in English**?

- Data: about 100 matched English–Bangla grade-school math problems from MGSM-Rev2.
- Tested models: free, open models only, run on our own machines.
- Simulated user and answer checker: one fixed open model.

**Settings** (same names as the base paper):

| Setting | What the model sees |
| --- | --- |
| FULL | The original problem in one message |
| CONCAT | All shards joined in one message |
| SHARDED | One shard per turn; the simulated user picks which shard to reveal next. Shard 1 always comes first. |
| SNOWBALL | Like SHARDED, but each turn repeats all earlier shards |

**Main result:**

```
Δ = (CONCAT − SHARDED) in Bangla − (CONCAT − SHARDED) in English
```

- Units are accuracy percentage points.
- Report Δ with a 95% bootstrap range.

## 2. Hard rules

1. **No paid API calls, ever.** This includes OpenAI, Azure, Anthropic and Google. If any code path would call one, disable it and tell me.
2. **Serving:** run models with **llama.cpp (`llama-server`)** behind an OpenAI-compatible endpoint. Do not use Ollama. llama.cpp should be installed already. I have been using it for thesis and for running Qwen as a daily driver.
3. **Don't edit upstream logic.** Keep the upstream repo pinned to one commit, as a git submodule or a vendored copy with the commit hash recorded. Add our code next to it, for example as an adapter for the model client.
4. **One config file** (`config.yaml`) is the single source of truth for:
   - model names and quantisation
   - endpoints and seeds
   - temperatures and number of runs
   - file paths
5. **Never invent numbers.** Every number in any report must come from a file the code wrote. If something didn't run, say so.
6. **Log everything:** one JSONL line per conversation, holding:
   - the setting, language, problem id and run id
   - the model, its quantisation and the seed
   - every turn's text, the extracted answer, and whether it was correct
   - the shard order used
7. **Ask me before you:**
   - accept any licence or terms (for example the Llama licence on Hugging Face)
   - download anything over 20 GB
   - delete data
   - change the research design
8. **Keep it simple.** Prefer small scripts over frameworks. Explain choices in plain words.

## 3. Hardware: detect, don't assume

Expected machines (verify them, don't trust this list):

- **Desktop:** RTX 5060 Ti 16 GB, 32 GB RAM, windows (this pc). WSL available.
- **Second GPU machine:** 8 GB (RTX 3070 but can rarely be used)
- **MacBook Pro:** M5 Pro, 24 GB unified memory (development machine; can also serve via llama.cpp Metal).

Known risk:

- At Q4, the simulator (**Qwen3.8-27B**) is probably about 16–17 GB, so it may not fit fully on the 16 GB GPU. I have an IQ3_XXS downloaded with an inference engine at this path: "G:\Agents".
- The simulator and a tested model must both be running during SHARDED conversations. We can create an hydrid setup for this if possible - the tested model can run on the mac and the simulator can run on this pc.

Measure the real memory use, then propose a placement plan. For example: the simulator on the Mac over the local network, and the tested models on the desktop and the 8 GB machine.

## Phase 1: set up the repository

1. **Repo layout:**

   ```
   upstream/   pinned base-paper code
   src/        our code
   data/
   configs/
   scripts/
   results/    git-ignored except summaries
   notebooks/
   README.md
   ```

2. **Python environment:** use `uv` or `venv` with pinned versions, and install upstream `requirements.txt` plus our extras.
3. **Build llama.cpp** with CUDA on Linux and Metal on Mac. Write one script, `scripts/serve.sh <model-key>`, that starts `llama-server` for a model named in `config.yaml`.
4. **Write `src/model_local.py`:** an OpenAI-compatible client that points at our `llama-server` URLs. Wire it into the upstream code so that:
   - the tested model calls go to our server
   - the simulated user, the strategy/answer extractor and the checker all go to the simulator server
   - every call that used to go to GPT-4o-mini now goes to our simulator
5. **Smoke test:** run the upstream **math** task on 3 problems × FULL and SHARDED × 1 run, using a small model (Llama-3.1-8B).

**Checkpoint 1.** Report:

- the layout tree
- the upstream commit hash
- the hardware you found and the placement plan
- the smoke-test log, plus one full SHARDED conversation printed in readable form
- any place where upstream still points to a paid API

## Phase 2: download the models

| Role | Model |
| --- | --- |
| Tested | Llama-3.1-8B-Instruct |
| Tested | Phi-4 (14B) |
| Tested | Gemma 4 12B |
| Tested | gpt-oss-20b |
| Simulator + checker | Qwen3.8-27B (thinking mode off) |

1. **Get GGUF weights** from the official publisher, or a well-known converter if no official GGUF exists. Record for each model:
   - the repo, file name, SHA256 and quantisation
   - the licence
   - Gemma 4 is already downloaded at: "G:\Code\MSc\abrar-thesis\models\gemma4"
2. **Quantisation:** default Q4_K_M. gpt-oss-20b can use its native MXFP4. Use the **same file for English and Bangla**; that is what keeps the comparison fair.
3. **Speed and memory test** on each model: tokens/sec and peak memory on its target machine, for a 2,000-token prompt plus a 300-token reply.
4. **Time estimate:** using the measured speeds, estimate the total hours for Phases 3 and 4.

**Checkpoint 2.** Show:

- a table: model, file, quantisation, licence, machine, memory, tokens/sec
- the time estimate
- anything that doesn't fit

## Phase 3: reproduce the base paper (math only)

The goal is to show our local setup behaves like theirs, not to match their numbers exactly. Their simulator was GPT-4o-mini; ours is Qwen3.8-27B.

1. **Data:** the upstream math items in `data/sharded_instructions_600.json`. Report how many there are; the paper says 103. See if we can add every dataset also? Just doing math seems underwhelming.
2. **Models:** Llama-3.1-8B-Instruct and Phi-4, which are both in the base paper.
3. **Runs:** FULL, CONCAT and SHARDED, 5 runs each, temperature 1.0 (as in the paper; confirm against the upstream defaults).
4. **Metrics:** as in the paper (§4.2):

   | Metric | How it's computed |
   | --- | --- |
   | Average accuracy (P) | Mean score across runs and problems |
   | Aptitude (A90) | 90th percentile of the scores across runs for each problem, then averaged over problems |
   | Unreliability (U = 90th − 10th percentile) | 90th minus 10th percentile of the scores across runs for each problem, then averaged over problems |

5. **Compare** with the paper's reported math numbers for these two models, side by side.
6. **Hand-check:** export 20 SHARDED conversations to a readable file so we can check the simulator for:
   - revealing too much
   - leaking the answer
   - marking answers wrong by mistake

**Checkpoint 3.** Show:

- our numbers vs. the paper's, in one table
- the simulator error notes
- the time taken

Do not continue if SHARDED is not clearly below FULL. Report it and stop.

## Phase 4: our extension (English vs. Bangla)

### 4a. Build the dataset

1. **Find MGSM-Rev2** (Peter et al., GEM 2026, "Mind the Gap… or Not?"). It holds 250 GSM8K problems in 11 languages and is licensed CC BY-SA 4.0. Show me the source before using it.
2. **Make two separate sets:**
   - **Main set:** about 100 problems. Prefer problems that overlap with the upstream math items, matched by question text and answer.
   - **Pilot set:** 50 problems, with no overlap with the main set.
3. **English shards:**
   - **Overlapping problems:** reuse the upstream shards, then check that the facts and answer match the MGSM-Rev2 English text.
   - **Other problems:** shard them with the upstream sharding prompts (`prompts/`), using the simulator model.
   - **Flag** anything that doesn't match, for a human to review.
4. **Bangla shards:**
   - Translate each English shard with the simulator model, keeping the same shard boundaries.
   - Export a review CSV with these columns: problem id, shard id, English, Bangla, answer, OK? (yes/no), fixed Bangla.
   - Native speakers fill it in; then merge their fixes back.
5. **Freeze:** save the final file with a SHA256 hash. Never edit it after main runs start.

**Checkpoint 4a.** Show:

- the counts
- the number of reused vs. new shards
- a 5-problem sample in both languages
- the review CSV path

### 4b. Pilot (pick the models)

1. Run each tested model on the 50 Bangla pilot problems in FULL, 3 runs.
2. **Keep a model only if its accuracy is ≥ 30%.** Below that, a model has too little room to drop. Excluded models are reported, not hidden.

**Checkpoint 4b.** Show the pilot table and which models pass.

### 4c. Main runs

1. Run each kept model × {English, Bangla} × {FULL, CONCAT, SHARDED} × 5 runs, on the frozen main set.
2. Run SNOWBALL on a fixed random 30 of the main problems, in both languages, with the same 30 for every model. Use 5 runs.
3. **Shard order:** keep the upstream rule (shard 1 first, then the simulator picks). Log the order used.
4. **Answer checking:** take the final number and normalise it before comparing:
   - convert Bangla digits ০–৯ to 0–9
   - remove thousands separators
   - strip units
   - compare as numbers

   Correct = exactly equal to the reference. A conversation ends on a correct answer or when the shards run out (the upstream rule).
5. **Make runs resumable:** a crash must not lose finished conversations.

### 4d. Analysis

1. **Main table:** P, A90 and U per model × language × setting.
2. **Losses and Δ:**
   - L_EN = CONCAT − SHARDED in English
   - L_BN = the same in Bangla
   - Δ = L_BN − L_EN, in percentage points
3. **95% bootstrap range for Δ:**
   - Resample **problems** with replacement, keeping each problem's English and Bangla runs together.
   - Use 10,000 resamples with a fixed seed.
4. **Read each result as:**

   | Δ range | Meaning |
   | --- | --- |
   | Entirely above 0 | More loss in Bangla |
   | Entirely below 0 | Less loss in Bangla |
   | Includes 0 | Difference unclear |

5. **SNOWBALL:** its gain over SHARDED on the same 30 problems, per language, with a bootstrap range.
6. **Hand-check:** export 30 random conversations per language for simulator errors, and report the error rate.
7. **Outputs:** plots of English vs. Bangla bars per setting, and a `results/summary.md` with every table, each one generated by a script.

**Checkpoint 4d.** Show the summary, the plots, the error rates and anything unexpected.

## Reporting style

- Plain English, short sentences, no jargon.
- At each checkpoint, cover:
  - what was done
  - what was found, with numbers from files
  - what failed or looks wrong
  - what you plan next
- Mark any guess as a guess.
