from typing import Optional


def validate_phone_digits(
    v: Optional[str], allow_none: bool = True, min_len: int = 12, max_len: int = 14
) -> Optional[str]:
    """Validate that phone number contains only digits and has allowed length.

    By default this enforces numeric-only and length between 12 and 14 (inclusive).

    Args:
        v: the value to validate
        allow_none: whether None is accepted
        min_len: minimum allowed length (inclusive)
        max_len: maximum allowed length (inclusive)

    Returns:
        The original value if valid.

    Raises:
        ValueError: if the value is invalid.
    """
    if v is None:
        if allow_none:
            return v
        raise ValueError("phone_number is required")
    if not isinstance(v, str):
        raise ValueError("phone_number must be a string of digits")
    if not v.isdigit():
        raise ValueError("phone_number must contain only digits")
    ln = len(v)
    if ln < min_len or ln > max_len:
        raise ValueError(
            f"phone_number length must be between {min_len} and {max_len} digits (got {ln})"
        )
    return v
