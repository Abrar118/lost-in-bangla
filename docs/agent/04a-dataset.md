# 04a. Build the English–Bangla dataset

Read `00-context.md` and `STATE.md` first. This phase only needs the simulator server, so it can run beside Phases 2 and 3.

## Tasks

1. **Find MGSM-Rev2.** Show a person the source (link, licence, version) **before** using it. Save the raw files under `data/raw/mgsm_rev2/`, with the source URL and download date.

2. **Measure the overlap first:** how many of the upstream math items are also MGSM-Rev2 problems? Match on question text and answer. Record the count in `STATE.md`.

3. **Two sets, no shared problems:**
   - **Main set:** about 100 problems. Include every overlapping problem.
   - **Pilot set:** 50 problems.

4. **English shards:**
   - **Overlapping problems:** reuse upstream's shards, then check that their facts and answer match the MGSM-Rev2 English text.
   - **Other problems:** make shards with upstream's math sharding prompts (`prompts/math/`) and its verification prompt (`prompts/lazification_verification.txt`), run on the simulator.
   - **Automatic checks:** shard 1 states the goal; all shards together hold every fact; the answer is unchanged.
   - Flag anything that fails, for a person to review.

5. **Bangla:**
   - Translate each English shard with the simulator, keeping the same shard boundaries.
   - Translate upstream's math instruction (system) message too.
   - Bangla FULL uses the MGSM-Rev2 Bangla text as it is.

6. **Review sheet:** a CSV with columns `problem_id, shard_id, english, bangla, answer, ok (yes/no), fixed_bangla, notes`.
   - Include the translated instruction message as one extra row.
   - Write a one-page plain-language guide for the native-speaker reviewers.
   - After review, merge their fixes back with a script.

7. **Freeze:** write `data/final/dataset.json`, record its SHA256 in `STATE.md`, and add `data/final/LICENSE` (CC BY-SA 4.0, crediting MGSM-Rev2, GSM8K and upstream). **Never edit it after main runs start.**

## Checkpoint 4a report
- counts: main, pilot, overlap, reused vs. new shard sets, flagged items
- a 5-problem sample in both languages
- the review CSV path and the reviewer guide path
- the frozen file path and hash, once frozen
