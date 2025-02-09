"""Test cases for utility functions."""

import string
from app.utils import generate_short_code


def test_generate_short_code_valid_length():
    """Test short code is generated with valid length."""
    length = 10
    res = generate_short_code(length)
    default_result = generate_short_code()

    assert len(res) == length
    assert len(default_result) == 6


def test_generate_short_code_valid_chars():
    """Test short code is generated with valid characters."""
    res = generate_short_code()
    chars = string.ascii_letters + string.digits

    assert all(c in chars for c in res)

def test_generate_short_code_unique():
    """Test short code is generated uniquely."""
    res1 = generate_short_code()
    res2 = generate_short_code()

    assert res1 != res2
    assert len(set([res1, res2])) == 2

def test_generate_short_code_with_original_url():
    """Test short code is generated with original URL."""
    original_url = "https://www.example.com"
    res = generate_short_code(original_url=original_url)

    assert res == generate_short_code(original_url=original_url)
    assert res != generate_short_code(original_url="https://www.example.com/other")
