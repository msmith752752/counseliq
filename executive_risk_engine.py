def calculate_executive_risk_score(ticker: str, sec_data: dict, ai_brief: dict, quiet_signal_data: dict) -> dict:
    """
    CounselIQ Executive Risk Severity Engine V1

    Converts filing deltas, leadership signals, and quiet signals into a single
    institutional-style executive risk severity score.
    """

    score = 0
    drivers = []

    quiet_level = quiet_signal_data.get("quiet_signal_level", "Unknown")
    quiet_signals = quiet_signal_data.get("quiet_signals", [])
    filing_changes = sec_data.get("notable_changes", [])
    leadership_score = ai_brief.get("leadership_signal_score", 50)

    # Quiet signal level weighting
    if quiet_level == "Critical":
        score += 35
        drivers.append("Critical quiet signal level detected")
    elif quiet_level == "High":
        score += 30
        drivers.append("High quiet signal level detected")
    elif quiet_level == "Elevated":
        score += 25
        drivers.append("Elevated quiet signal level detected")
    elif quiet_level == "Moderate":
        score += 15
        drivers.append("Moderate quiet signal level detected")
    elif quiet_level == "Calm":
        score += 5
        drivers.append("Quiet signal level currently calm")

    # Number and severity of quiet signals
    high_severity_count = 0
    medium_severity_count = 0

    for signal in quiet_signals:
        severity = signal.get("severity", "").lower()

        if severity == "high":
            high_severity_count += 1
        elif severity == "medium":
            medium_severity_count += 1

    if high_severity_count:
        score += high_severity_count * 10
        drivers.append(f"{high_severity_count} high-severity quiet signal(s) detected")

    if medium_severity_count:
        score += medium_severity_count * 5
        drivers.append(f"{medium_severity_count} medium-severity quiet signal(s) detected")

    # Filing comparison change weighting
    for change in filing_changes:
        change_lower = change.lower()

        if "risk language increased" in change_lower:
            score += 15
            drivers.append(change)

        if "new risk-related terms" in change_lower:
            score += 15
            drivers.append(change)

        if "liquidity" in change_lower or "debt" in change_lower:
            score += 10
            drivers.append(change)

        if "confidence/growth language increased" in change_lower:
            score -= 5
            drivers.append("Positive offset: confidence/growth language increased")

    # Leadership score adjustment
    if leadership_score is not None:
        if leadership_score < 50:
            score += 15
            drivers.append("Leadership signal score is weak")
        elif leadership_score < 65:
            score += 8
            drivers.append("Leadership signal score is cautious")
        elif leadership_score >= 80:
            score -= 8
            drivers.append("Positive offset: leadership signal score is strong")

    # Keep score bounded
    score = max(0, min(score, 100))

    if score >= 80:
        level = "Severe"
    elif score >= 65:
        level = "Elevated"
    elif score >= 45:
        level = "Moderate"
    elif score >= 25:
        level = "Watch"
    else:
        level = "Low"

    interpretation = _build_executive_risk_interpretation(
        ticker=ticker,
        score=score,
        level=level,
        drivers=drivers,
    )

    return {
        "executive_risk_score": score,
        "executive_risk_level": level,
        "executive_risk_drivers": drivers,
        "executive_risk_interpretation": interpretation,
    }


def _build_executive_risk_interpretation(ticker: str, score: int, level: str, drivers: list) -> str:
    """
    Builds a concise institutional-style interpretation.
    """

    ticker = ticker.upper()

    if level == "Severe":
        return (
            f"{ticker} shows a severe executive-risk profile. Multiple leadership, filing, "
            "and quiet-signal indicators appear to be moving in a more defensive or uncertain "
            "direction. CounselIQ would treat this as a high-priority narrative-risk candidate."
        )

    if level == "Elevated":
        return (
            f"{ticker} shows an elevated executive-risk profile. Filing language, leadership tone, "
            "or quiet-signal activity suggests uncertainty may be increasing beneath the surface. "
            "This may be relevant for monitoring volatility, analyst sentiment, or institutional repricing risk."
        )

    if level == "Moderate":
        return (
            f"{ticker} shows a moderate executive-risk profile. CounselIQ detected some cautionary "
            "signals, but the evidence does not yet suggest a severe narrative deterioration."
        )

    if level == "Watch":
        return (
            f"{ticker} is in watch status. Current leadership and filing signals do not indicate major "
            "deterioration, but there are enough minor changes to keep the company on the radar."
        )

    return (
        f"{ticker} currently shows a low executive-risk profile based on the available filing, "
        "leadership, and quiet-signal data."
    )