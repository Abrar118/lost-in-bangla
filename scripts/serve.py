"""Start llama-server for the simulator or one tested model, using configs/config.yaml.

    python scripts/serve.py simulator
    python scripts/serve.py gemma4-12b
    python scripts/serve.py gemma4-12b --dry-run     # print the command only
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from config import load_config, machine, server_spec  # noqa: E402


def build_command(cfg, key):
    spec = server_spec(cfg, key)
    m = machine()
    exe = cfg["llama_server"][m]
    model_file = spec["files"].get(m)
    if not model_file:
        raise SystemExit(f"No model file for {key!r} on {m}. Add it under files.{m} in configs/config.yaml.")
    s = spec["server"]
    alias = cfg["simulator"]["key"] if key == "simulator" else key
    cmd = [exe, "-m", model_file, "--alias", alias, "--host", s["host"], "--port", str(s["port"]),
           "-c", str(s["ctx_size"]), "-ngl", str(s["gpu_layers"]), "-np", str(s["parallel"]), "--jinja"]
    return cmd + [str(a) for a in s.get("extra_args", [])], exe, model_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key", help="'simulator' or a tested-model key from config.yaml")
    ap.add_argument("--dry-run", action="store_true", help="print the command and stop")
    args = ap.parse_args()
    cmd, exe, model_file = build_command(load_config(), args.key)
    print(" ".join(cmd))
    if args.dry_run:
        return
    for p in (exe, model_file):
        if not Path(p).exists():
            raise SystemExit(f"Not found: {p}")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
