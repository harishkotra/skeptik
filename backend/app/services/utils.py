from __future__ import annotations

import json
import re
from urllib.parse import urlparse


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def extract_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def compact_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2, default=str)
