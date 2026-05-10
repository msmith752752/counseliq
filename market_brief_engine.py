from datetime import datetime

from sec_engine import get_sec_filing_summary
from ai_engine import generate_executive_brief
from quiet_signals_engine import build_quiet_signals


DEFAULT_BRIEF_TICKERS = ["AAPL", "NVDA", "MSFT", "JPM", "AMZN"]


def _severity_rank(level: str) -> int:
    """
    Converts quiet signal level into a sortable rank.
    Higher number = higher concern.
    """
    if not level:
        return 0

    level = level.lower()

    if "critical" in level:
        return 5
    if "high" in level:
        return 4
    if "elevated" in level:
        return 3
    if "moderate" in level:
        return 2
    if "low" in level:
        return 1

    return 0


def _safe_get_company_intelligence(ticker: str):
    """
    Runs the real CounselIQ company intelligence stack for one ticker.
    If one ticker fails, the entire market brief should not fail.
    """
    try:
        sec_data = get_sec_filing_summary(ticker)
        ai_brief = generate_executive_brief(ticker, sec_data)
        quiet_signal_data = build_quiet_signals(ticker, sec_data, ai_brief)

        quiet_level = quiet_signal_data.get("quiet_signal_level", "Unknown")

        return {
            "ticker": ticker.upper(),
            "company": ticker.upper(),
            "quiet_signal_level": quiet_level,
            "severity_rank": _severity_rank(quiet_level),
            "leadership_signal_score": ai_brief.get("leadership_signal_score"),
            "leadership_signal_label": ai_brief.get("leadership_signal_label"),
            "leadership_tone": ai_brief.get("leadership_tone"),
            "quiet_signal_summary": quiet_signal_data.get("quiet_signal_summary"),
            "quiet_signals": quiet_signal_data.get("quiet_signals", []),
            "counseliq_interpretation": ai_brief.get("counseliq_interpretation"),
            "selected_filing": sec_data.get("selected_filing"),
            "selected_filing_url": sec_data.get("selected_filing_url"),
            "previous_comparable_filing": sec_data.get("previous_comparable_filing"),
            "filing_changes": sec_data.get("notable_changes", []),
            "status": "ok",
        }

    except Exception as error:
        return {
            "ticker": ticker.upper(),
            "company": ticker.upper(),
            "quiet_signal_level": "Unavailable",
            "severity_rank": 0,
            "leadership_signal_score": None,
            "leadership_signal_label": "Unavailable",
            "leadership_tone": "Unavailable",
            "quiet_signal_summary": "CounselIQ could not complete analysis for this ticker.",
            "quiet_signals": [],
            "counseliq_interpretation": f"Analysis unavailable due to: {str(error)}",
            "selected_filing": None,
            "selected_filing_url": None,
            "previous_comparable_filing": None,
            "filing_changes": [],
            "status": "error",
        }


def generate_market_brief(tickers=None):
    """
    CounselIQ Morning Intelligence Brief Engine V2

    Pulls real company intelligence from the existing CounselIQ pipeline:
    SEC Filing -> AI Brief -> Quiet Signals Engine

    Then ranks companies by quiet signal severity so the dashboard can show
    the highest-risk narrative shifts first.
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tickers_to_review = tickers or DEFAULT_BRIEF_TICKERS

    company_briefs = [
        _safe_get_company_intelligence(ticker)
        for ticker in tickers_to_review
    ]

    ranked_company_briefs = sorted(
        company_briefs,
        key=lambda item: item.get("severity_rank", 0),
        reverse=True,
    )

    elevated_risk_signals = [
        item for item in ranked_company_briefs
        if item.get("severity_rank", 0) >= 3
    ]

    moderate_watchlist = [
        item for item in ranked_company_briefs
        if item.get("severity_rank", 0) == 2
    ]

    lower_risk_or_unavailable = [
        item for item in ranked_company_briefs
        if item.get("severity_rank", 0) <= 1
    ]

    top_risk = ranked_company_briefs[0] if ranked_company_briefs else None

    if top_risk and top_risk.get("severity_rank", 0) >= 3:
        summary = (
            f"CounselIQ reviewed {len(tickers_to_review)} companies and detected "
            f"the highest quiet-signal concern in {top_risk['ticker']} "
            f"({top_risk['quiet_signal_level']})."
        )
    else:
        summary = (
            f"CounselIQ reviewed {len(tickers_to_review)} companies and did not detect "
            "a major elevated quiet-signal cluster in the current watchlist."
        )

    return {
        "generated_at": current_time,
        "brief_type": "CounselIQ Morning Intelligence Brief",
        "version": "0.2.0",
        "tickers_reviewed": [ticker.upper() for ticker in tickers_to_review],
        "market_environment": {
            "market_regime": "Pending live market environment integration",
            "counseliq_interpretation": (
                "This version focuses on company-level executive narrative risk. "
                "Futures, rates, VIX, earnings, and news catalysts will be added in later modules."
            ),
        },
        "top_quiet_signal": top_risk,
        "elevated_risk_signals": elevated_risk_signals,
        "moderate_watchlist": moderate_watchlist,
        "lower_risk_or_unavailable": lower_risk_or_unavailable,
        "ranked_company_briefs": ranked_company_briefs,
        "counseliq_summary": summary,
    }