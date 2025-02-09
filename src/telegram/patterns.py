ALLOWED_CHARACTERS = r"\ &,!\w\[\]+-"
QUERY_PATTERN = rf"^(r\/)?[{ALLOWED_CHARACTERS}]+$"
QUERY_PATTERN_LIMITED_CHARS = rf"^(r\/)?[{ALLOWED_CHARACTERS}]{{1,60}}$"
PRICE_PATTERN = r"^\d+([,\.]\d{1,2})?$"
