"""Dependency-free helpers for preserving last-good pace-analysis sessions."""

TYRE_COMPOUNDS = ("SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET")


def fastest_lap_compound(lap):
    """Read the compound from the selected lap, not the driver's stint mode."""
    compound = lap.get("Compound")
    return compound if isinstance(compound, str) and compound in TYRE_COMPOUNDS else None


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


def matching_session_articles(articles, driver_name, team, label):
    """Return newest-first articles about this driver in this session."""
    session_terms = {
        "Practice 1": ("fp1", "practice 1", "opening practice", "first practice"),
        "Practice 2": ("fp2", "practice 2", "second practice"),
        "Practice 3": ("fp3", "practice 3", "third practice", "final practice"),
        "Qualifying": ("qualifying",),
        "Sprint Qualifying": ("sprint qualifying", "sq1", "sq2", "sq3"),
        "Sprint": ("sprint",),
        "Race": ("race report", "grand prix report"),
    }.get(label, ())
    surname = driver_name.split()[-1].lower() if driver_name else ""
    team_word = (team or "").split()[0].lower()
    if not surname:
        return []

    matches = []
    for article in reversed(articles):
        title = article.get("title", "")
        title_lower = title.lower()
        if session_terms and not any(term in title_lower for term in session_terms):
            continue
        combined = " ".join([title] + article.get("paragraphs", [])).lower()
        if surname in title_lower and team_word in combined:
            matches.append(article)
    return matches
