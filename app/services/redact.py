import re

_EMAIL = re.compile(r"\b\S+@\S+\.\S+\b")
_PHONE = re.compile(r"\+?\d[\d\-\s()]{7,}\d")
_NAME  = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")

def redact(text: str) -> str:
    if not text:
        return ""
    t = _EMAIL.sub("[[EMAIL]]", text)
    t = _PHONE.sub("[[PHONE]]", t)
    def _name_guard(m):
        s = m.group(1)
        if any(x in s for x in ["University","Institute","College","Technologies","Inc","Ltd"]):
            return s
        return "[[NAME]]"
    return _NAME.sub(_name_guard, t)
