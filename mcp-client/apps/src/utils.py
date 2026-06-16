import json

def clean_unicode(text: str) -> str:
    return text.encode("ascii", errors="ignore").decode("ascii")

def clean_val(val):
    if isinstance(val, dict):
        return {k: clean_val(v) for k, v in val.items()}
    if isinstance(val, list):
        return [clean_val(v) for v in val]
    if isinstance(val, str):
        return clean_unicode(val.replace("\n", " "))
    return val

def extract_text(content):
    text = []
    for data in content:
        try:
            parsed = json.loads(data.text)
            text.append(json.dumps(clean_val(parsed)))
        except Exception:
            text.append(data.text.replace("\n", " ").strip())
    return " | ".join(text)