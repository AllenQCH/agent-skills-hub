"""Acceptance QA API test template.

Run:
    ACCEPTANCE_API_BASE_URL=http://localhost:8000 python -m pytest .qa-agent/tests/api -q
"""

import os

import requests


BASE_URL = os.environ.get("ACCEPTANCE_API_BASE_URL", "http://localhost:8000")


def test_tc_003_health_or_contract_smoke():
    """TC-003 API contract smoke check.

    Replace `/health` with a product-specific endpoint and assert the acceptance-level contract.
    """
    response = requests.get(f"{BASE_URL}/health", timeout=10)

    assert response.status_code in {200, 204}


def test_tc_004_invalid_request_is_rejected_safely():
    """TC-004 invalid input should not mutate data and should return a safe error."""
    # Example:
    # response = requests.post(f"{BASE_URL}/orders", json={}, timeout=10)
    # assert response.status_code in {400, 422}
    # assert "traceback" not in response.text.lower()
    assert BASE_URL
