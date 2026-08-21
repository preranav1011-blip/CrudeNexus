import types

from app.data import loaders


class DummyResp:
    def __init__(self, payload):
        self._payload = payload
        self.ok = True
        self.status_code = 200

    def json(self):
        return self._payload


def test_fetch_gdelt_events_monkeypatch(monkeypatch):
    # Sample payload that mimics a GDELT-like response with 'articles'
    sample = {"articles": [{"url": "http://example.com/1", "title": "Test Event", "date": "2026-08-20", "summary": "Sample"}]}

    def fake_get(url, params=None, timeout=10):
        assert url is not None
        return DummyResp(sample)

    # Patch requests.get used inside loaders
    monkeypatch.setattr(loaders, 'requests', types.SimpleNamespace(get=fake_get))

    events = loaders.fetch_gdelt_events(keywords=["India"], hours_back=1, limit=5)
    assert isinstance(events, list)
    assert len(events) == 1
    assert events[0].get('title') == "Test Event"
