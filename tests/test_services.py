"""Unit tests for the services layer (no database involved)."""

import pytest

from app.services import encode_base62, generate_short_code, is_allowed_url


class TestEncodeBase62:
    def test_zero(self):
        assert encode_base62(0) == "0"

    def test_known_values(self):
        # Alphabet order: digits, then lowercase, then uppercase
        assert encode_base62(9) == "9"
        assert encode_base62(10) == "a"
        assert encode_base62(35) == "z"
        assert encode_base62(36) == "A"
        assert encode_base62(61) == "Z"
        # 62 must roll over to "10"
        assert encode_base62(62) == "10"

    def test_roundtrip(self):
        from app.services import ALPHABET

        for n in (1, 17, 12345, 2**32):
            code = encode_base62(n)
            restored = 0
            for ch in code:
                restored = restored * len(ALPHABET) + ALPHABET.index(ch)
            assert restored == n

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            encode_base62(-1)


class TestGenerateShortCode:
    def test_length(self):
        code = generate_short_code(8)
        assert len(code) == 8

    def test_default_length(self):
        assert len(generate_short_code()) == 6

    def test_charset_and_uniqueness(self):
        import string

        valid = set(string.ascii_letters + string.digits)
        codes = {generate_short_code() for _ in range(50)}
        assert all(set(code) <= valid for code in codes)
        # 50 random 6-char codes: a collision would be suspicious
        assert len(codes) == 50


class TestIsAllowedUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com/path?q=1",
            "https://sub.domain.org:8080/p/a?x=1#frag",
        ],
    )
    def test_valid(self, url):
        assert is_allowed_url(url)

    @pytest.mark.parametrize(
        "url",
        [
            "ftp://example.com",  # disallowed scheme
            "javascript:alert(1)",  # XSS attempt
            "example.com",  # no scheme
            "https://",  # empty host
            "https://exa mple.com/x",  # whitespace
            "https://example.com/x\nEvil: y",  # header injection
            "",
        ],
    )
    def test_invalid(self, url):
        assert not is_allowed_url(url)
