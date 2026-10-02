"""Dependency-free helpers for identifying and summarising practice long runs."""

import statistics

MIN_LONG_RUN_LAPS = 5


def _consecutive_groups(samples):
    groups, current = [], []
    for sample in sorted(samples, key=lambda row: row["lap_number"]):
        if current and sample["lap_number"] != current[-1]["lap_number"] + 1:
            groups.append(current)
            current = []
        current.append(sample)
    if current:
        groups.append(current)
    return groups


def _linear_slope(xs, ys):
    mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    if not denominator:
        return 0.0
    return sum((x - mean_x) * (y - mean_y)
               for x, y in zip(xs, ys)) / denominator


def _without_outliers(samples):
    times = [row["lap_time"] for row in samples]
    median = statistics.median(times)
    deviations = [abs(value - median) for value in times]
    mad = statistics.median(deviations)
    tolerance = max(1.5, 3 * 1.4826 * mad)
    return [row for row in samples
            if abs(row["lap_time"] - median) <= tolerance]


def analyse_long_run_samples(samples, min_laps=MIN_LONG_RUN_LAPS):
    """Return credible continuous long runs from ordered clean-lap samples.

    A qualifying simulation normally alternates push and cooldown laps. Requiring
    consecutive timed laps prevents its isolated push laps from being presented as
    race pace. A robust median/MAD pass then removes traffic or obvious mistakes;
    at least 70% of the continuous sequence must survive.
    """
    runs = []
    for group in _consecutive_groups(samples):
        if len(group) < min_laps:
            continue
        retained = _without_outliers(group)
        if (len(retained) < min_laps
                or len(retained) / len(group) < 0.7):
            continue
        times = [row["lap_time"] for row in retained]
        lap_numbers = [row["lap_number"] for row in retained]
        std_dev = statistics.pstdev(times) if len(times) > 1 else 0.0
        if std_dev > 2.0:
            continue
        if len(retained) >= 8 and std_dev <= 1.0:
            confidence = "high"
        elif len(retained) >= 6 and std_dev <= 1.5:
            confidence = "medium"
        else:
            confidence = "low"
        tyre_lives = [row.get("tyre_life") for row in retained
                      if row.get("tyre_life") is not None]
        runs.append({
            "laps": len(retained),
            "raw_laps": len(group),
            "excluded_laps": len(group) - len(retained),
            "lap_start": min(lap_numbers),
            "lap_end": max(lap_numbers),
            "avg_time": round(statistics.mean(times), 3),
            "median_time": round(statistics.median(times), 3),
            "std_dev": round(std_dev, 3),
            "pace_trend": round(_linear_slope(lap_numbers, times), 3),
            "tyre_life_start": min(tyre_lives) if tyre_lives else None,
            "tyre_life_end": max(tyre_lives) if tyre_lives else None,
            "confidence": confidence,
        })
    return runs
