"""Dependency-free helpers for preserving last-good pace-analysis sessions."""


def merge_completed_sessions(existing, refreshed, completed_codes, session_order):
    """Return completed sessions in display order, preferring fresh results."""
    existing_by_code = {
        session.get("session"): session
        for session in existing
        if session.get("session")
    }
    refreshed_by_code = {
        session.get("session"): session
        for session in refreshed
        if session.get("session")
    }
    completed = set(completed_codes)
    merged = []
    for code in session_order:
        if code not in completed:
            continue
        session = refreshed_by_code.get(code) or existing_by_code.get(code)
        if session:
            merged.append(session)
    return merged
