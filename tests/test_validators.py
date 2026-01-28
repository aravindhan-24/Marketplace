from source.utility.validators import (
    validate_str,
    validate_int,
    validate_number,
    validate_enum,
    validate_url,
    validate_url_array,
)


def test_validate_string():
    v = validate_str({"required": True})
    assert v("abc")
    assert not v("")


def test_validate_int():
    v = validate_int({"required": True, "min": 5})
    assert v("10")
    assert not v("2")
    assert not v("abc")


def test_validate_number():
    v = validate_number({"required": False})
    assert v("10.5")
    assert not v("x")


def test_validate_enum():
    v = validate_enum({"allowed": ["A", "B"]})
    assert v("A")
    assert not v("C")


def test_validate_url():
    v = validate_url({"required": True})
    assert v("https://example.com")
    assert not v("ftp://example.com")


def test_validate_url_array():
    v = validate_url_array({"required": False})
    assert v("https://a.com | https://b.com")
    assert not v("invalid-url")
