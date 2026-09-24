"""
Tests for the mock tools (no LLM calls needed).
Run: python -m pytest tests/test_tools.py -v
"""

from tools.order_tools import check_order_status
from tools.billing_tools import calculate_billing
from tools.status_tools import check_service_status


# ── Order Tools ───────────────────────────────────────────────────

def test_order_found():
    result = check_order_status("ORD-4521")
    assert result["status"] == "shipped"
    assert "tracking" in result


def test_order_refund_pending():
    result = check_order_status("ORD-2201")
    assert result["status"] == "refund_pending"
    assert "refund_amount" in result


def test_order_not_found():
    result = check_order_status("ORD-9999")
    assert "error" in result


def test_order_case_insensitive():
    result = check_order_status("ord-4521")
    assert result["status"] == "shipped"


# ── Billing Tools ─────────────────────────────────────────────────

def test_billing_pro_within_limit():
    result = calculate_billing("pro", 50)
    assert result["total"] == "$29.99"
    assert result["overage_gb"] == 0


def test_billing_pro_with_overage():
    result = calculate_billing("pro", 200)
    assert result["overage_gb"] == 100
    assert result["overage_cost"] == "$25.00"
    assert result["total"] == "$54.99"


def test_billing_free_with_overage():
    result = calculate_billing("free", 10)
    assert result["overage_gb"] == 5
    assert result["total"] == "$2.50"


def test_billing_enterprise_500gb():
    result = calculate_billing("enterprise", 500)
    assert result["overage_gb"] == 0
    assert result["total"] == "$99.99"


def test_billing_unknown_plan():
    result = calculate_billing("premium", 100)
    assert "error" in result


def test_billing_case_insensitive():
    result = calculate_billing("Pro", 50)
    assert result["plan"] == "pro"


# ── Service Status Tools ──────────────────────────────────────────

def test_service_status_returns_all_services():
    result = check_service_status()
    assert "overall" in result
    assert "services" in result
    assert "Compute" in result["services"]
    assert "Storage" in result["services"]


def test_service_status_storage_degraded():
    result = check_service_status()
    assert result["services"]["Storage"]["status"] == "degraded"
