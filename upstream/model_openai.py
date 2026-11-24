# OUR EDIT: the original file called the paid OpenAI / Azure API. It is replaced by a thin
# link to our local client (src/model_local.py). See upstream/OUR_CHANGES.md.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from model_local import format_messages, generate, generate_json  # noqa: E402,F401
