from __future__ import annotations

import calendar
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}


def clean_text(value: str | None, max_length: int | None = None) -> str | None:
    if not value:
        return None
    text = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if max_length and len(text) > max_length:
        return text[: max_length - 1].rstrip() + "…"
    return text


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        raise ValueError("article URL must be an absolute HTTP(S) URL")
    filtered = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lower = key.lower()
        if lower in TRACKING_QUERY_KEYS or lower.startswith(TRACKING_QUERY_PREFIXES):
            continue
        filtered.append((key, value))
    filtered.sort(key=lambda item: (item[0].lower(), item[1]))
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(filtered), ""))


def make_content_hash(
    title: str,
    source_slug: str,
    published_at: datetime | None,
    canonical_url: str,
) -> str:
    # Independent from the canonical-URL constraint: if a publisher changes a story URL,
    # the same normalized title from the same source on the same publication date still
    # resolves to the same fingerprint. For undated entries we fall back to the URL to
    # avoid false positives on recurring headlines.
    date_key = published_at.date().isoformat() if published_at else canonical_url
    normalized_title = re.sub(r"\s+", " ", title).strip().casefold()
    payload = f"{source_slug}|{date_key}|{normalized_title}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def entry_datetime(entry) -> datetime | None:
    value = entry.get("published_parsed") or entry.get("updated_parsed")
    if not value:
        return None
    return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc)


def extract_image_url(entry) -> str | None:
    media = entry.get("media_content") or entry.get("media_thumbnail") or []
    if media and isinstance(media, list):
        url = media[0].get("url")
        if url:
            return url
    for enclosure in entry.get("enclosures", []):
        if str(enclosure.get("type", "")).startswith("image/") and enclosure.get("href"):
            return enclosure["href"]
    return None
