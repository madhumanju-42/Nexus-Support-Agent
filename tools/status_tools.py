"""Mock service status check tool."""


def check_service_status() -> dict:
    """Check current NexusCloud service status."""
    return {
        "overall": "partial_outage",
        "services": {
            "Compute": {"status": "operational", "uptime": "99.98%"},
            "Storage": {
                "status": "degraded",
                "message": "Elevated latency in US-East region",
            },
            "CDN": {"status": "operational", "uptime": "99.99%"},
            "API Gateway": {"status": "operational", "uptime": "99.95%"},
            "Dashboard": {"status": "operational", "uptime": "99.97%"},
        },
        "last_updated": "2026-05-19T14:30:00Z",
    }
