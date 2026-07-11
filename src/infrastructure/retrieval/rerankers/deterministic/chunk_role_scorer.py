def role_score(role: str) -> float:
    return {
        "atomic_evidence": 14.0,
        "asset_companion": 6.0,
        "context_companion": 2.0,
        "overview_companion": -6.0,
    }.get(role, 0.0)
