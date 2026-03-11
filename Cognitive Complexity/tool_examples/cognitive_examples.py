"""Examples with nested logic for cognitive-complexity tooling."""


def triage_order(total: int, member: bool, express: bool, stock: int) -> str:
    if total > 100:
        if stock > 0:
            if member or express:
                return "ship-now"
            return "standard-queue"
        return "backorder"
    if member:
        if express and stock > 0:
            return "ship-now"
        return "member-queue"
    return "normal-queue"


def review_alert(level: str, retries: int, acknowledged: bool) -> str:
    if level == "critical":
        if retries > 3:
            return "escalate"
        if acknowledged:
            return "monitor"
        return "page"
    if level == "warning":
        if retries > 1 and not acknowledged:
            return "follow-up"
        return "watch"
    return "log"


def refactor_candidate(values: list[int]) -> list[int]:
    output = []
    for value in values:
        if value % 2 == 0:
            output.append(value * 2)
    return list(output)
