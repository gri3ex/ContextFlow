def classify_content(text):
    text_stripped = text.strip()
    if not text_stripped:
        return "empty"
    if text_stripped.startswith("http://") or text_stripped.startswith("https://") or text_stripped.startswith("www."):
        return "link"
    if any(err in text_stripped for err in ["Exception", "Error:", "Traceback", "Permission denied", "command not found"]):
        return "terminal/error"
    code_keywords = ["def ", "class ", "import ", "#include", "fn ", "fmt.", "console.log", "SELECT ", "public class", "var ", "let ", "const ", "print(", "return "]
    has_syntax = any(kw in text_stripped for kw in code_keywords)
    has_brackets = "{" in text_stripped and "}" in text_stripped
    has_indents = "\n    " in text_stripped or "\n\t" in text_stripped
    if has_syntax or (has_brackets and len(text_stripped.splitlines()) > 1) or (has_indents and len(text_stripped.splitlines()) > 1):
        return "code"
    return "text"