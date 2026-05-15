def build_institutional_positioning_intelligence(ticker: str) -> dict:
    """
    CounselIQ Institutional Positioning Engine V1

    Goal:
    Provide institutional-style interpretation around
    hedge fund positioning, thematic concentration,
    and capital allocation behavior.

    NOTE:
    This is currently a framework layer with placeholder
    intelligence. Real 13F ingestion and institutional
    tracking will be added later.
    """

    ticker = ticker.upper()

    positioning_level = "Neutral"

    positioning_signals = []

    institutional_interpretation = (
        "CounselIQ is building institutional positioning intelligence "
        "to identify where sophisticated capital allocators may be "
        "concentrating exposure before broader market repricing occurs."
    )

    if ticker in ["NVDA", "MSFT", "AMZN"]:

        positioning_level = "Accumulating"

        positioning_signals = [
            "AI infrastructure theme exposure increasing",
            "Large-cap institutional concentration remains elevated",
            "Technology leadership positioning appears intact",
        ]

        institutional_interpretation = (
            "Institutional positioning suggests continued concentration "
            "around AI infrastructure, hyperscaler dominance, "
            "and large-cap technology leadership themes."
        )

    elif ticker in ["JPM", "GS", "MS"]:

        positioning_level = "Macro Sensitive"

        positioning_signals = [
            "Financial sector positioning tied to rates environment",
            "Institutional exposure may shift with macro expectations",
            "Capital markets sensitivity remains elevated",
        ]

        institutional_interpretation = (
            "Institutional positioning appears increasingly dependent "
            "on interest-rate expectations, liquidity conditions, "
            "and broader macroeconomic direction."
        )

    elif ticker in ["LMT", "RTX", "NOC", "VSAT"]:

        positioning_level = "Government / Defense Focus"

        positioning_signals = [
            "Defense and government exposure increasing",
            "Geopolitical sensitivity elevated",
            "Institutional interest tied to strategic infrastructure themes",
        ]

        institutional_interpretation = (
            "CounselIQ detects positioning associated with "
            "defense, communications infrastructure, "
            "and government-related strategic themes."
        )

    return {
        "institutional_positioning_level": positioning_level,
        "institutional_positioning_signals": positioning_signals,
        "institutional_positioning_interpretation": institutional_interpretation,
    }