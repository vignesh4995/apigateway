import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    print("Setting up before test")
    yield
    print("Tearing down after test")

def test_root():
    response = client.get("/")
    print("test_root response:", response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API gateway!"}

def test_rate_limit():
    for _ in range(9):
        response = client.get("/")
        print("test_rate_limit response (under limit):", response.json())
        assert response.status_code == 200
    
    response = client.get("/")
    print("test_rate_limit response (over limit):", response.json())
    assert response.status_code == 429

# def test_process_claims(mocker):
#     mock_response = MagicMock()
#     mock_response.status = 200
#     mock_response.text = "claims processed successfully"
#     mocker.patch("aiohttp.ClientSession.post", return_value=mock_response)

#     with open("claim_1234.csv", "rb") as file:
#         response = client.post("/claims/", files={"file": ("claim_1234.csv", file, "text/csv")})
#     print("test_process_claims response:", response.json())
#     assert response.status_code == 200
#     assert "claims processed successfully" in response.json()

# def test_read_top_10_providers(mocker):
#     mock_response = MagicMock()
#     mock_response.status_code = 200
#     mock_response.json.return_value = [{"name": "Provider 1", "npi": "0000000001"}]
#     mocker.patch("httpx.AsyncClient.get", return_value=mock_response)

#     response = client.get("/providers/top10")
#     print("test_read_top_10_providers response:", response.json())
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)
