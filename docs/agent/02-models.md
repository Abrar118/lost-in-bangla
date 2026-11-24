# 02. Get the models and measure them

Read `00-context.md` and `STATE.md` first.

| Role | Model | Quant |
| --- | --- | --- |
| Tested | Llama-3.1-8B-Instruct | Q4_K_M |
| Tested | Phi-4 (14B) | Q4_K_M |
| Tested | Gemma 4 12B | Q4_K_M (already on disk; see 00-context) |
| Tested | gpt-oss-20b | native MXFP4 |
| Simulator + checker | Qwen3.8-27B | IQ3_S (already on disk) |

## Tasks

1. **Get the GGUF files**, from the official publisher or a well-known converter if there is no official GGUF.
   - **Ask** before accepting any licence (Llama is gated).
   - **Ask** before copying files onto the Mac.
   - Record repo, file name, SHA256, quantisation and licence in `STATE.md` and `config.yaml`.

2. **Speed and memory test** for each model on its target machine:
   - Use a 2,000-token prompt plus a 300-token reply, in **English and in Bangla**. Bangla uses more tokens, so measure both.
   - Record prompt speed and reply speed (tokens/sec) and peak memory.
   - For the simulator, also time one full simulator turn (user reply + answer check) over the network.

3. **Token limit check:** run a few Bangla FULL problems per model. Confirm the token limit in `config.yaml` doesn't cut replies off. For gpt-oss, check at its configured reasoning level.

4. **Time estimate** for Phases 3, 4b and 4c, from the measured speeds.
   - Show the arithmetic: number of conversations × average turns × seconds per turn.
   - Give the estimate twice: with **5** SHARDED runs and with **10**.
   - Give a separate rough estimate for `05-extra-tasks.md`.

## Checkpoint 2 report
- a table: model, file, quant, licence, machine, memory, prompt and reply tokens/sec (English and Bangla)
- the time estimate (5 vs 10 SHARDED runs), and the team's choice
- anything that didn't fit or was cut off
