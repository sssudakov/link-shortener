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
