from re import compile


text_pattern = compile(r"[a-zA-Z0-9]")


def check_text(text: str) -> bool:
    return bool(text_pattern.findall(text))
