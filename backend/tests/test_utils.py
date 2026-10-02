from app.ingestion.classifier import classify
from datetime import datetime, timezone

from app.ingestion.utils import canonicalize_url, clean_text, make_content_hash


def test_canonicalize_url_removes_tracking_and_fragment():
    value = canonicalize_url(
        "HTTPS://Example.com/story/?utm_source=newsletter&id=7&fbclid=abc#section"
    )
    assert value == "https://example.com/story?id=7"


def test_clean_text_strips_html():
    assert clean_text("<p>Hello <strong>world</strong></p>") == "Hello world"


def test_classifier_can_assign_multiple_categories():
    categories = classify(
        "Ransomware gang exploits CVE-2026-1234",
        "A security flaw was used in an extortion campaign.",
    )
    assert "ransomware" in categories
    assert "vulnerability" in categories


def test_content_hash_is_independent_of_url_for_dated_same_source_story():
    published = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
    first = make_content_hash("Same Story", "publisher", published, "https://example.com/a")
    second = make_content_hash("Same   Story", "publisher", published, "https://example.com/b")
    assert first == second
