from re import compile


text_pattern = compile(r"[a-zA-Z0-9]")
email_pattern = compile(r"\w+@\w+.\w+")


def check_text(text: str) -> bool:
    return bool(text_pattern.findall(text))


def check_email(email: str) -> bool:
    return email_pattern.fullmatch(email) is not None
