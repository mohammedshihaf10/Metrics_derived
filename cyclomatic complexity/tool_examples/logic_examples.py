"""Pure Python examples for CFG, path, and condition-oriented tools."""


def route_order(total: int, member: bool, express: bool) -> str:
    """Pick a delivery path based on order size and flags."""

    if total > 100:
        if member or express:
            return "priority"
        return "standard"
    if member and express:
        return "priority"
    return "economy"


def approval_bucket(score: int, income: int, vip: bool) -> str:
    """A compact decision tree with compound predicates."""

    if score >= 700 and (income >= 50_000 or vip):
        return "approve"
    if score >= 620 and income >= 30_000:
        return "manual"
    return "reject"
