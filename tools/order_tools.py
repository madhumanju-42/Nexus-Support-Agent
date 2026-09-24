"""Mock order status lookup tool."""


# Simulated order database
_ORDERS = {
    "ORD-4521": {
        "status": "shipped",
        "product": "NexusCloud Pro Plan - Annual",
        "date": "2026-05-10",
        "tracking": "1Z999AA10123456784",
        "estimated_delivery": "2026-05-22",
    },
    "ORD-3892": {
        "status": "processing",
        "product": "NexusCloud Enterprise Add-on",
        "date": "2026-05-17",
        "tracking": None,
        "estimated_delivery": "2026-05-25",
    },
    "ORD-2201": {
        "status": "refund_pending",
        "product": "NexusCloud Storage 500GB",
        "date": "2026-04-28",
        "refund_amount": "$49.99",
        "refund_eta": "5-7 business days",
    },
}


def check_order_status(order_id: str) -> dict:
    """Look up order status by order ID."""
    order_id = order_id.strip().upper()
    return _ORDERS.get(order_id, {"error": f"Order {order_id} not found"})
