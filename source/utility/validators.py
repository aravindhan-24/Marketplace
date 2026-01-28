from urllib.parse import urlparse

def is_not_empty(v):
    return v is not None and str(v).strip() != ""


def validate_str(rule):
    required = rule.get("required", False)
    max_len = rule.get("maxLen")

    def validator(v):
        if not is_not_empty(v):
            return not required
        if max_len and len(str(v)) > max_len:
            return False
        return True

    return validator


def validate_int(rule):
    required = rule.get("required", False)
    min_v = rule.get("min")

    def validator(v):
        if not is_not_empty(v):
            return not required
        try:
            n = int(v)
        except ValueError:
            return False
        if min_v is not None and n < min_v:
            return False
        return True

    return validator


def validate_number(rule):
    required = rule.get("required", False)
    min_v = rule.get("min")

    def validator(v):
        if not is_not_empty(v):
            return not required
        try:
            n = float(v)
        except ValueError:
            return False
        if min_v is not None and n < min_v:
            return False
        return True

    return validator


def validate_enum(rule):
    required = rule.get("required", False)
    allowed = set(rule.get("allowed", []))

    def validator(v):
        if not is_not_empty(v):
            return not required
        return v in allowed

    return validator


def validate_url(rule):
    required = rule.get("required", False)

    def validator(v):
        if not is_not_empty(v):
            return not required
        p = urlparse(v)
        return p.scheme in ("http", "https") and bool(p.netloc)

    return validator

def validate_url_array(rule):
    required = rule.get("required", False)

    def validator(v):
        v = (v or "").strip()

        if v == "":
            return not required

        parts = [x.strip() for x in v.split("|") if x.strip()]
        if not parts:
            return not required

        for url in parts:
            p = urlparse(url)
            if p.scheme not in ("http", "https") or not p.netloc:
                return False

        return True

    return validator


TYPE_DISPATCHER = {
    "string": validate_str,
    "int": validate_int,
    "number": validate_number,
    "enum": validate_enum,
    "url": validate_url,
    "urlArray": validate_url_array,
}
