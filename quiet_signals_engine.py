def build_quiet_signals(ticker: str, sec_data: dict, ai_brief: dict):
    """
    CounselIQ Quiet Signals Engine V1.

    This layer converts filing comparison data into plain-English
    behind-the-scenes corporate behavior signals.

    Goal:
    Help identify narrative, risk, confidence, and strategic shifts
    that may matter before they become obvious in price action or headlines.
    """

    ticker = ticker.upper()
    comparison = sec_data.get("filing_comparison", {}) or {}

    signals = []

    tone_shift = comparison.get("tone_shift", "")
    risk_delta = comparison.get("risk_language_delta", 0) or 0
    confidence_delta = comparison.get("confidence_language_delta", 0) or 0
    liquidity_delta = comparison.get("liquidity_debt_language_delta", 0) or 0
    capital_delta = comparison.get("capital_allocation_language_delta", 0) or 0

    new_risk_terms = comparison.get("new_risk_terms", []) or []
    new_liquidity_terms = comparison.get("new_liquidity_debt_terms", []) or []
    new_capital_terms = comparison.get("new_capital_allocation_terms", []) or []

    lower_new_risk_terms = [term.lower() for term in new_risk_terms]

    def add_signal(title, severity, category, explanation, investment_readthrough):
        signals.append(
            {
                "title": title,
                "severity": severity,
                "category": category,
                "explanation": explanation,
                "investment_readthrough": investment_readthrough,
            }
        )

    # 1. Defensive tone / risk expansion
    if risk_delta >= 50 or "defensive" in tone_shift.lower():
        add_signal(
            title="Defensive Language Increasing",
            severity="High" if risk_delta >= 50 else "Medium",
            category="Tone / Risk",
            explanation=(
                f"{ticker} showed a meaningful increase in risk-related language "
                f"versus the prior comparable filing."
            ),
            investment_readthrough=(
                "This may indicate management is disclosing more uncertainty beneath the surface. "
                "For stocks and options, this can matter because increasing risk language may precede "
                "higher volatility, analyst caution, or institutional repricing."
            ),
        )

    elif risk_delta >= 20:
        add_signal(
            title="Risk Language Building",
            severity="Medium",
            category="Risk",
            explanation=(
                f"{ticker} risk language increased by {risk_delta} references compared with the prior filing."
            ),
            investment_readthrough=(
                "Moderate risk-language expansion can suggest the company is beginning to acknowledge "
                "new or growing pressures before they become headline events."
            ),
        )

    # 2. New regulatory / legal terms
    regulatory_terms = {
        "regulatory",
        "regulation",
        "compliance",
        "investigation",
        "litigation",
        "lawsuit",
        "legal",
        "antitrust",
        "enforcement",
    }

    if any(term in regulatory_terms for term in lower_new_risk_terms):
        add_signal(
            title="Regulatory or Legal Exposure Emerging",
            severity="High",
            category="Legal / Regulatory",
            explanation=(
                "New legal or regulatory-related terminology appeared in the latest comparable filing."
            ),
            investment_readthrough=(
                "New regulatory language can be an early warning sign for headline risk, multiple compression, "
                "or implied volatility expansion. This is especially relevant before earnings or major legal updates."
            ),
        )

    # 3. Disruption / business model pressure
    disruption_terms = {
        "disruption",
        "competitive pressure",
        "competition",
        "substitution",
        "technological change",
        "pricing pressure",
    }

    if any(term in lower_new_risk_terms for term in disruption_terms):
        add_signal(
            title="Business Disruption Language Detected",
            severity="Medium",
            category="Competitive Position",
            explanation=(
                "The latest filing introduced or emphasized language tied to disruption, competition, "
                "or business model pressure."
            ),
            investment_readthrough=(
                "This may suggest management is acknowledging external pressure that could affect margins, "
                "growth expectations, or investor confidence."
            ),
        )

    # 4. Confidence weakening
    if confidence_delta <= -10:
        add_signal(
            title="Confidence Language Weakening",
            severity="High" if confidence_delta <= -25 else "Medium",
            category="Confidence",
            explanation=(
                f"Confidence-related language declined by {abs(confidence_delta)} references versus the prior filing."
            ),
            investment_readthrough=(
                "A decline in confidence language can signal reduced management conviction. "
                "This can matter for earnings expectations, forward guidance, and options volatility."
            ),
        )

    # 5. Confidence increasing while risk also increasing = mixed message
    if confidence_delta > 0 and risk_delta > 30:
        add_signal(
            title="Mixed Management Signal",
            severity="Medium",
            category="Narrative Tension",
            explanation=(
                "Both confidence language and risk language increased versus the prior comparable filing."
            ),
            investment_readthrough=(
                "This may suggest management is still presenting operational strength while also expanding "
                "risk disclosure. Mixed signals can create uncertainty and may be important before earnings."
            ),
        )

    # 6. Liquidity / debt pressure
    if liquidity_delta >= 10 or new_liquidity_terms:
        add_signal(
            title="Liquidity or Debt Language Increasing",
            severity="Medium",
            category="Balance Sheet",
            explanation=(
                "Liquidity or debt-related language increased compared with the prior comparable filing."
            ),
            investment_readthrough=(
                "More liquidity or debt discussion may indicate balance sheet sensitivity, funding pressure, "
                "or a more cautious capital posture."
            ),
        )

    # 7. Capital allocation shift
    if abs(capital_delta) >= 10 or new_capital_terms:
        if capital_delta > 0:
            title = "Capital Allocation Discussion Increasing"
            readthrough = (
                "More capital allocation language may indicate increased emphasis on cash, debt, dividends, "
                "buybacks, or shareholder return strategy."
            )
        else:
            title = "Capital Allocation Discussion Declining"
            readthrough = (
                "Reduced capital allocation language may suggest less emphasis on shareholder returns, "
                "buybacks, dividends, or capital strategy versus the prior filing."
            )

        add_signal(
            title=title,
            severity="Medium",
            category="Capital Allocation",
            explanation=(
                f"Capital allocation language changed by {capital_delta} references versus the prior filing."
            ),
            investment_readthrough=readthrough,
        )

    # 8. Broad strategic uncertainty
    negative_pressure_count = 0

    if risk_delta >= 20:
        negative_pressure_count += 1
    if confidence_delta <= -10:
        negative_pressure_count += 1
    if liquidity_delta >= 10:
        negative_pressure_count += 1
    if any(term in regulatory_terms for term in lower_new_risk_terms):
        negative_pressure_count += 1
    if "defensive" in tone_shift.lower():
        negative_pressure_count += 1

    if negative_pressure_count >= 3:
        add_signal(
            title="Strategic Uncertainty Increasing",
            severity="High",
            category="Strategic Risk",
            explanation=(
                "Multiple behind-the-scenes signals moved in a more cautious direction at the same time."
            ),
            investment_readthrough=(
                "When several quiet signals deteriorate together, the market may eventually reprice the company "
                "even before a single obvious headline explains the move."
            ),
        )

    # Fallback if no signals are detected
    if not signals:
        add_signal(
            title="No Major Quiet Signal Detected",
            severity="Low",
            category="Baseline",
            explanation=(
                "CounselIQ did not detect a major behind-the-scenes filing shift in the latest comparable filing."
            ),
            investment_readthrough=(
                "This does not mean the stock will not move. It means the current filing comparison does not show "
                "a strong hidden narrative, risk, liquidity, or confidence shift."
            ),
        )

    # Overall quiet signal summary
    high_count = len([signal for signal in signals if signal["severity"] == "High"])
    medium_count = len([signal for signal in signals if signal["severity"] == "Medium"])

    if high_count >= 2:
        overall_level = "Elevated"
    elif high_count == 1 or medium_count >= 2:
        overall_level = "Watch"
    else:
        overall_level = "Calm"

    summary = (
        f"CounselIQ detected {len(signals)} quiet signal(s) for {ticker}. "
        f"Overall hidden-signal level: {overall_level}."
    )

    return {
        "quiet_signal_level": overall_level,
        "quiet_signal_summary": summary,
        "quiet_signals": signals,
    }