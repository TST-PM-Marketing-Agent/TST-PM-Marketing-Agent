import json
import os
from urllib import error, request


def _extract_json_array(text: str):
    return json.loads(text[text.index("["):text.rindex("]") + 1])


def _extract_json_object(text: str):
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def _try_ollama(prompt: str):
    try:
        from ollama import chat

        res = chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        return res.message.content.strip()
    except Exception:
        return None


def _try_openai_compatible(prompt: str):
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not base_url or not api_key:
        return None
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
    ).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"].strip()
    except (error.URLError, error.HTTPError, KeyError, ValueError, TimeoutError):
        return None


def llm_json_array(prompt: str):
    text = _try_ollama(prompt)
    if text:
        try:
            return _extract_json_array(text)
        except Exception:
            pass
    text = _try_openai_compatible(prompt)
    if text:
        try:
            return _extract_json_array(text)
        except Exception:
            pass
    return None


def llm_json_object(prompt: str):
    text = _try_ollama(prompt)
    if text:
        try:
            return _extract_json_object(text)
        except Exception:
            pass
    text = _try_openai_compatible(prompt)
    if text:
        try:
            return _extract_json_object(text)
        except Exception:
            pass
    return None
