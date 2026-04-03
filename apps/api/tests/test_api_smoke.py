def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_response(client):
    response = client.get("/dashboard", headers={"x-admin-token": "replace-with-token"})
    assert response.status_code == 200
    payload = response.json()
    assert "accounts" in payload
    assert "recent_logs" in payload
