def count_keyword_hits(text: str, keywords: list):
    """
    Count how often a group of keywords appears in text.
    """

    lower_text = text.lower()

    hits = 0

    for keyword in keywords:
        hits += lower_text.count(keyword.lower())

    return hits


def get_signal_label(score: int):
    """
    Convert numeric Leadership Signal Score into a plain-English label.
    """

    if score >= 80:
        return "Strong"
    elif score >= 65:
        return "Stable"
    elif score >= 50:
        return "Cautious"
    else:
        return "Concerning"


def generate_executive_brief(ticker: str, sec_data: dict):
    """
    Phase 1 local intelligence engine.

    This does not use an external AI API yet.
    It analyzes extracted SEC narrative chunks using keyword/theme detection.
    """

    narrative_chunks = sec_data.get("narrative_chunks", [])
    combined_text = " ".join(narrative_chunks)
    lower_text = combined_text.lower()

    risk_keywords = [
        "risk",
        "uncertain",
        "exposure",
        "fluctuations",
        "litigation",
        "regulatory",
        "material adverse",
        "competition",
        "supply",
        "foreign exchange",
        "interest rate",
        "macroeconomic",
        "inflation",
        "decline",
        "adverse",
        "weakness",
    ]

    growth_keywords = [
        "growth",
        "customers",
        "services",
        "products",
        "market",
        "demand",
        "revenue",
        "innovation",
        "investment",
        "expansion",
        "opportunity",
        "platform",
        "ecosystem",
    ]

    capital_allocation_keywords = [
        "repurchase",
        "dividend",
        "debt",
        "cash",
        "marketable securities",
        "capital",
        "shareholders",
        "liquidity",
        "free cash flow",
        "return capital",
    ]

    confidence_keywords = [
        "strong",
        "record",
        "increased",
        "improved",
        "resilient",
        "continued",
        "successful",
        "leading",
        "positive",
    ]

    risk_score = count_keyword_hits(combined_text, risk_keywords)
    growth_score = count_keyword_hits(combined_text, growth_keywords)
    capital_score = count_keyword_hits(combined_text, capital_allocation_keywords)
    confidence_score = count_keyword_hits(combined_text, confidence_keywords)

    leadership_signal_score = 60

    leadership_signal_score += min(growth_score, 20)
    leadership_signal_score += min(capital_score, 10)
    leadership_signal_score += min(confidence_score, 10)
    leadership_signal_score -= min(risk_score, 25)

    leadership_signal_score = max(0, min(100, leadership_signal_score))
    leadership_signal_label = get_signal_label(leadership_signal_score)

    if risk_score > growth_score and risk_score > capital_score:
        leadership_tone = "Risk-aware / defensive"
    elif growth_score >= risk_score and growth_score >= capital_score:
        leadership_tone = "Operational / growth-focused"
    elif capital_score > 0:
        leadership_tone = "Capital allocation focused"
    else:
        leadership_tone = "Neutral / insufficient narrative data"

    strategic_focus = "Unable to determine strategic focus from available filing narrative."

    if growth_score > 0:
        strategic_focus = (
            "Management language appears focused on products, services, customers, "
            "market conditions, innovation, and operating performance."
        )

    capital_allocation = "No strong capital allocation signal detected."

    if capital_score > 0:
        capital_allocation = (
            "Filing language includes capital allocation themes such as cash, debt, "
            "liquidity, dividends, repurchases, shareholder returns, or marketable securities."
        )

    risk_themes = []

    for keyword in risk_keywords:
        if keyword.lower() in lower_text:
            risk_themes.append(keyword)

    risk_themes = list(dict.fromkeys(risk_themes))

    executive_summary = (
        f"{ticker.upper()} filing narrative was reviewed across "
        f"{len(narrative_chunks)} extracted business/management chunks. "
        f"CounselIQ detected {risk_score} risk-theme references, "
        f"{growth_score} growth/operations-theme references, "
        f"{capital_score} capital-allocation references, and "
        f"{confidence_score} confidence-language references."
    )

    leadership_signal_explanation = (
        f"CounselIQ assigns {ticker.upper()} a Leadership Signal Score of "
        f"{leadership_signal_score}/100, classified as {leadership_signal_label}. "
        "This early score weighs growth/operations language, capital allocation language, "
        "confidence language, and risk-heavy disclosure language."
    )

    counseliq_interpretation = (
        "CounselIQ is evolving from an SEC filing summarizer into a corporate behavioral intelligence engine. "
        "The platform is designed to identify behind-the-scenes changes in leadership tone, risk disclosure, "
        "confidence language, liquidity language, legal exposure, and strategic positioning. "
        "The goal is not to replace investment judgment, but to surface hidden corporate signals that may help "
        "explain or anticipate stock and options movement before they become obvious in headlines."
    )

    return {
        "executive_summary": executive_summary,
        "leadership_signal_score": leadership_signal_score,
        "leadership_signal_label": leadership_signal_label,
        "leadership_signal_explanation": leadership_signal_explanation,
        "leadership_tone": leadership_tone,
        "strategic_focus": strategic_focus,
        "capital_allocation": capital_allocation,
        "risk_themes": risk_themes,
        "counseliq_interpretation": counseliq_interpretation,
    }