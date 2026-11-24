"""OpenAI-compatible client for our own llama-server endpoints.

Replaces upstream's model_openai.py (which needed paid API keys). No API key, no paid service.

Routing:
  generate_json(...)        -> simulator server (user simulator, turn check, answer extraction).
  generate(..., model=KEY)  -> tested-model server; KEY must be in config.yaml tested_models.
Sampling, token limit and timeout come from configs/config.yaml, not from the caller.
Every call is recorded; the runner reads the records with end_conversation().
"""
import hashlib
import json
import re
import threading
import time
import urllib.error
import urllib.request

from config import load_config

CFG = load_config()
_local = threading.local()


def format_messages(messages, variables={}):
    """Same as upstream: fill [[KEY]] placeholders in the last user message."""
    last_user_msg = [msg for msg in messages if msg["role"] == "user"][-1]
    for k, v in variables.items():
        key_string = f"[[{k}]]"
        if key_string not in last_user_msg["content"]:
            print(f"[prompt] Key {k} not found in prompt; effectively ignored")
        assert type(v) == str, f"[prompt] Variable {k} is not a string"
        last_user_msg["content"] = last_user_msg["content"].replace(key_string, v)
    keys_still_in_prompt = re.findall(r"\[\[([^\]]+)\]\]", last_user_msg["content"])
    if len(keys_still_in_prompt) > 0:
        print(f"[prompt] The following keys were not replaced: {keys_still_in_prompt}")
    return messages


# ---- per-conversation recording and seeds -------------------------------------------------

def start_conversation(seed_key):
    """Call before a conversation. seed_key = 'problem|setting|language|run'."""
    _local.seed_key, _local.calls = seed_key, []


def end_conversation():
    calls, _local.calls, _local.seed_key = _local.calls, None, None
    return calls


def _seed(role, purpose, index):
    text = f"{CFG['seed_salt']}|{_local.seed_key}|{role}|{purpose}|{index}"
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) & 0x7FFFFFFF


# ---- helpers -------------------------------------------------------------------------------

_THINK = re.compile(r"^\s*<think>(.*?)(</think>|$)", re.DOTALL)


def split_thinking(content, reasoning):
    """Keep thinking text out of the visible reply. Use the server's field if present, else <think> tags."""
    if reasoning:
        return content, reasoning
    m = _THINK.match(content or "")
    if m:
        return content[m.end():].lstrip(), m.group(1).strip()
    return content, None


def _post(url, body, timeout):
    req = urllib.request.Request(url + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def generate(messages, model=None, timeout=None, max_retries=None, temperature=1.0, is_json=False,
             return_metadata=False, max_tokens=None, variables={}, purpose=None):
    """Same signature as upstream's generate. timeout and max_tokens from the caller are ignored (config wins)."""
    if is_json:
        role, spec = "simulator", None
        url, max_out = CFG["endpoints"]["simulator"], CFG["simulator_max_tokens"]
        body = {"model": CFG["simulator"]["key"], "temperature": temperature,
                "response_format": {"type": "json_object"}, **CFG["simulator_sampling"], **CFG["simulator"]["request_extra"]}
        sampling = {"temperature": temperature, **CFG["simulator_sampling"]}
    else:
        if model not in CFG["tested_models"]:
            raise ValueError(f"generate() needs a tested-model key from config.yaml, got {model!r}")
        role = "tested"
        url, max_out = CFG["endpoints"]["tested"], CFG["tested_max_tokens"]
        body = {"model": model, **CFG["tested_sampling"], **CFG["tested_models"][model]["request_extra"]}
        sampling = dict(CFG["tested_sampling"])

    messages = format_messages(messages, variables)
    calls = getattr(_local, "calls", None)
    index = len(calls) if calls is not None else 0
    seed = _seed(role, purpose, index) if calls is not None else None
    body.update({"messages": messages, "max_tokens": max_out, "seed": seed})
    if seed is None:
        del body["seed"]

    retries = max_retries or CFG["request_retries"]
    for attempt in range(1, retries + 1):
        try:
            resp = _post(url, body, CFG["request_timeout_s"])
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == retries:
                raise Exception(f"Failed to get a response from the {role} server at {url}: {e}")
            time.sleep(4)

    choice = resp["choices"][0]
    msg = choice["message"]
    text, reasoning = split_thinking(msg.get("content") or "", msg.get("reasoning_content"))
    usage = resp.get("usage", {})
    record = {"purpose": purpose, "role": role, "model": resp.get("model"),  # name the server itself reports (its --alias)
              "seed": seed, "sampling": sampling, "max_tokens": max_out, "prompt": messages, "output": text,
              "reasoning_text": reasoning, "finish_reason": choice.get("finish_reason"),
              "tokens": usage.get("completion_tokens"), "prompt_tokens": usage.get("prompt_tokens")}
    if calls is not None:
        calls.append(record)

    if not return_metadata:
        return text
    return {"message": text, "total_tokens": usage.get("total_tokens"), "prompt_tokens": usage.get("prompt_tokens"),
            "prompt_tokens_cached": 0, "completion_tokens": usage.get("completion_tokens"),
            "total_usd": 0.0, "reasoning": reasoning, "finish_reason": choice.get("finish_reason")}


def generate_json(messages, model=None, **kwargs):
    response = generate(messages, model, is_json=True, **kwargs)
    response["message"] = json.loads(response["message"])
    return response
