
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock  import patch

client = TestClient(app)


def test_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["version"] == "1.0.0"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_invalid_item():
    response = client.post(
        "/items",
        json={
            "name": "",
            "quantity": -1,
            "price": -10
        }
    )
    assert response.status_code == 422


from unittest.mock import patch


def test_visits():
    with patch("app.main.redis_client") as mock_redis:
        mock_redis.incr.return_value = 1

        response = client.get("/visits")

    assert response.status_code == 200
    assert response.json()["visits"] == 1
    mock_redis.incr.assert_called_once_with(
        "portfolio:visits"
    )
