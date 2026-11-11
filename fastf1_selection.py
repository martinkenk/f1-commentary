import datetime


POST_RACE_WINDOW_DAYS = 7


def active_analysis_slugs(gps, today):
    selected = [gp for gp in gps if gp.get("status") == "live"]
    past = [gp for gp in gps if gp.get("status") == "past" and gp.get("race_date")]
    if past:
        latest = max(past, key=lambda gp: gp["race_date"])
        race_date = datetime.date.fromisoformat(latest["race_date"])
        if 0 <= (today - race_date).days <= POST_RACE_WINDOW_DAYS:
            selected.append(latest)
    return {gp["dir"] for gp in selected}
