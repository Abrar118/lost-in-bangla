# Shared state

Each agent reads this first and updates it before stopping. Only facts and file paths go here, no opinions. Every number names the file it came from.

## Upstream
- Commit: `c865793fe34a929d316119b0451d01bd9183bcfd` (`upstream/UPSTREAM_COMMIT`; matches `git ls-remote` on 2026-11-24)
- Our edits: see `upstream/OUR_CHANGES.md`

## Endpoints
- Simulator (Windows): not running yet. `configs/config.yaml` `endpoints.simulator` is a placeholder (`127.0.0.1:8081`); set it to the desktop's LAN address. Start with `python scripts/serve.py simulator`.
- Tested models (Mac): `http://127.0.0.1:8080/v1`. Start with `python scripts/serve.py <model-key>`.

## Model files
| Model | File | SHA256 | Quant | Licence | Machine |
| --- | --- | --- | --- | --- | --- |
| gemma4-12b | `/Users/orion-abrar/Code/masters/Thesis/models/gemma4/gemma-4-12B-it-Q4_K_M.gguf` (read in place; Windows copy at `G:/Code/MSc/abrar-thesis/models/gemma4/`) | `3962624dcd25b947d889dc9ae1bf275b61db6cd4dbe694057f34fffef1671509` (Mac copy; `shasum -a 256`, 2026-11-24) | Q4_K_M | not checked yet | Mac |
| qwen3.8-27b-iq3_s (simulator) | `G:/Agents/models/Qwen3.8-27B-GSQ-RCO-IQ3_S.gguf` | not measured | IQ3_S | not checked yet | Windows |

## Counts
- Upstream math items: 103 (`upstream/data/sharded_instructions_600.json`, items with `task == "math"`)
- Overlap between upstream math and MGSM-Rev2: _(not checked yet)_

## Measured on the Mac (Phase 1)
- Gemma 4 12B Q4_K_M, context 16,384, all layers on GPU: about 13.3 GB total in use with `--cache-ram 0` (11.7 GB wired GPU memory from `vm_stat`, 1.56 GB process from `footprint`). Without `--cache-ram 0`, llama-server's RAM prompt cache (default 8 GiB) grows on top, reaching ~20 GB+. An earlier figure of 8.2 GB (`ps` RSS) was wrong: it misses GPU memory.
- Gemma generation speed about 30 tokens/s (`results/serve_gemma.log`, not in git).
- Gemma 4 12B writes thinking text by default (returned as `reasoning_content`).

## Dataset freeze
- File: _(path)_
- SHA256: _(hash)_
- Frozen on: _(date)_

## Decisions made after 2026-11-24
_(date, decision, who approved)_
- 2026-11-24: `correct_ours` stays `null` until Phase 4 (user reviewed this assumption: right).
- 2026-11-24: Gemma file used in place from the Thesis folder, not copied (user reviewed: right).
- 2026-11-24: placeholder limits: tested reply 4,096 tokens, simulator reply 1,024 tokens (user reviewed: right). Phase 2 should check the cut-off rate.
- 2026-11-24: JSON calls always go to the simulator; plain chat calls must name a tested-model key (user reviewed: right).

## Phase status
| Phase | Status | Report |
| --- | --- | --- |
| 01 setup | Code done; dry run passed with a stand-in simulator. **Real smoke test waiting on the Windows simulator and firewall approval.** | `docs/agent/reports/01-setup.md` |
