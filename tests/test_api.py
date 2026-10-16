"""End-to-end API tests through the FastAPI test client."""

from app.database import SessionLocal
from app.models import Link


def fetch_clicks(code: str) -> int:
    with SessionLocal() as db:
        return int(db.query(Link).filter_by(code=code).one().clicks)


class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCreateShortLink:
    def test_creates_short_link(self, client):
        response = client.post("/api/links", json={"url": "https://example.com"})
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://example.com"
        assert data["clicks"] == 0
        assert len(data["code"]) == 6
        assert data["short_url"].endswith(f"/{data['code']}")

    def test_unique_codes(self, client):
        codes = {
            client.post("/api/links", json={"url": "https://example.com"}).json()["code"]
            for _ in range(5)
        }
        assert len(codes) == 5

    def test_rejects_bad_url(self, client):
        for url in ("ftp://example.com", "example.com", "", "https://"):
            response = client.post("/api/links", json={"url": url})
            assert response.status_code == 422, url

    def test_rejects_too_long_url(self, client):
        response = client.post("/api/links", json={"url": "https://x.com/" + "a" * 5000})
        assert response.status_code == 422


class TestRedirect:
    def _create(self, client, url):
        return client.post("/api/links", json={"url": url}).json()["code"]

    def test_redirects_to_target(self, client):
        code = self._create(client, "https://example.com/page")
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "https://example.com/page"

    def test_clicks_are_counted(self, client):
        code = self._create(client, "https://example.com")
        for _ in range(3):
            client.get(f"/{code}", follow_redirects=False)
        assert fetch_clicks(code) == 3

    def test_unknown_code_404(self, client):
        response = client.get("/zzzzzz", follow_redirects=False)
        assert response.status_code == 404


class TestStats:
    def test_stats_reflect_clicks(self, client):
        code = client.post("/api/links", json={"url": "https://example.com"}).json()["code"]
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)
        response = client.get(f"/api/links/{code}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == code
        assert data["url"] == "https://example.com"
        assert data["clicks"] == 2
        assert data["created_at"]

    def test_stats_for_unknown_code(self, client):
        assert client.get("/api/links/zzzzzz/stats").status_code == 404
