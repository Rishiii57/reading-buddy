"""REQ-SPOKEN-ONBOARDING: Buddy's spoken hint on the reading page (no API calls)."""
from fastapi.testclient import TestClient

from backend.main import app
from backend.phrases import PHRASES


def test_every_language_has_the_reader_hint():
    for lang, p in PHRASES.items():
        assert p.get("reader_hint"), lang
    assert set(PHRASES["en-IN"]) == set(PHRASES["hi-IN"]) == set(PHRASES["gu-IN"])


def test_phrase_endpoint_rejects_unknown_keys():
    c = TestClient(app)
    assert c.get("/api/phrase/en-IN/no_such_phrase").status_code == 404
    assert c.get("/api/phrase/xx-XX/reader_hint").status_code == 404
