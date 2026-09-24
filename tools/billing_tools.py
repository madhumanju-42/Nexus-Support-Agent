"""Mock billing calculation tool."""


_PLANS = {
    "free": {"base": 0, "included_gb": 5, "overage_per_gb": 0.50},
    "pro": {"base": 29.99, "included_gb": 100, "overage_per_gb": 0.25},
    "enterprise": {"base": 99.99, "included_gb": 500, "overage_per_gb": 0.10},
}


def calculate_billing(plan: str, usage_gb: float) -> dict:
    """Calculate estimated billing based on plan and usage."""
    p = _PLANS.get(plan.strip().lower())
    if not p:
        return {"error": f"Unknown plan: {plan}. Valid plans: free, pro, enterprise"}

    overage = max(0, usage_gb - p["included_gb"])
    overage_cost = overage * p["overage_per_gb"]
    total = p["base"] + overage_cost

    return {
        "plan": plan.strip().lower(),
        "base_cost": f"${p['base']:.2f}",
        "included_gb": p["included_gb"],
        "usage_gb": usage_gb,
        "overage_gb": overage,
        "overage_cost": f"${overage_cost:.2f}",
        "total": f"${total:.2f}",
    }
