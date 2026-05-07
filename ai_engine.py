def count_keyword_hits(text: str, keywords: list):
    """
    Count how often a group of keywords appears in text.
    """

    lower_text = text.lower()

    hits = 0

    for keyword in keywords:
        hits += lower_text.count(keyword.lower())

    return hits


def generate_executive_brief(ticker: str, sec_data: dict):
    """
    Phase 1 local intelligence engine.

    This does not use an external AI API yet.
    It analyzes extracted SEC narrative chunks using keyword/theme detection.
    """

    narrative_chunks = sec_data.get("narrative_chunks", [])
    combined_text = " ".join(narrative_chunks)

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
    ]

    risk_score = count_keyword_hits(combined_text, risk_keywords)
    growth_score = count_keyword_hits(combined_text, growth_keywords)
    capital_score = count_keyword_hits(combined_text, capital_allocation_keywords)

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
        strategic_focus = "Management language appears focused on products, services, customers, market conditions, and operating performance."

    capital_allocation = "No strong capital allocation signal detected."

    if capital_score > 0:
        capital_allocation = "Filing language includes capital allocation themes such as cash, debt, liquidity, dividends, repurchases, or marketable securities."

    risk_themes = []

    for keyword in risk_keywords:
        if keyword.lower() in combined_text.lower():
            risk_themes.append(keyword)

    risk_themes = list(dict.fromkeys(risk_themes))

    executive_summary = (
        f"{ticker.upper()} filing narrative was reviewed across "
        f"{len(narrative_chunks)} extracted business/management chunks. "
        f"CounselIQ detected {risk_score} risk-theme references, "
        f"{growth_score} growth/operations-theme references, and "
        f"{capital_score} capital-allocation references."
    )

    counseliq_interpretation = (
        "CounselIQ is beginning to convert raw SEC filings into structured executive intelligence. "
        "This early local engine uses narrative chunk extraction and theme detection; later versions can add true AI analysis, "
        "quarter-over-quarter comparison, executive tone shifts, and boardroom signal interpretation."
    )

    return {
        "executive_summary": executive_summary,
        "leadership_tone": leadership_tone,
        "strategic_focus": strategic_focus,
        "capital_allocation": capital_allocation,
        "risk_themes": risk_themes,
        "counseliq_interpretation": counseliq_interpretation,
    }