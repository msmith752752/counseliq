from datetime import datetime

from sec_engine import get_sec_filing_summary
from ai_engine import generate_executive_brief
from quiet_signals_engine import build_quiet_signals
from executive_risk_engine import calculate_executive_risk_score


DEFAULT_BRIEF_TICKERS = ["AAPL", "NVDA", "MSFT", "JPM", "AMZN"]


def _severity_rank(level: str) -> int:

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

    try:

        sec_data = get_sec_filing_summary(ticker)

        ai_brief = generate_executive_brief(
            ticker,
            sec_data
        )

        quiet_signal_data = build_quiet_signals(
            ticker,
            sec_data,
            ai_brief
        )

        executive_risk = calculate_executive_risk_score(
            ticker,
            sec_data,
            ai_brief,
            quiet_signal_data
        )

        quiet_level = quiet_signal_data.get(
            "quiet_signal_level",
            "Unknown"
        )

        return {

            "ticker": ticker.upper(),

            "company": ticker.upper(),

            "quiet_signal_level": quiet_level,

            "severity_rank": _severity_rank(
                quiet_level
            ),

            "leadership_signal_score":
            ai_brief.get(
                "leadership_signal_score"
            ),

            "leadership_signal_label":
            ai_brief.get(
                "leadership_signal_label"
            ),

            "leadership_tone":
            ai_brief.get(
                "leadership_tone"
            ),

            "quiet_signal_summary":
            quiet_signal_data.get(
                "quiet_signal_summary"
            ),

            "quiet_signals":
            quiet_signal_data.get(
                "quiet_signals",
                []
            ),

            "counseliq_interpretation":
            ai_brief.get(
                "counseliq_interpretation"
            ),

            "selected_filing":
            sec_data.get(
                "selected_filing"
            ),

            "selected_filing_url":
            sec_data.get(
                "selected_filing_url"
            ),

            "previous_comparable_filing":
            sec_data.get(
                "previous_comparable_filing"
            ),

            "filing_changes":
            sec_data.get(
                "notable_changes",
                []
            ),

            # NEW Executive Risk Layer

            "executive_risk_score":
            executive_risk[
                "executive_risk_score"
            ],

            "executive_risk_level":
            executive_risk[
                "executive_risk_level"
            ],

            "executive_risk_drivers":
            executive_risk[
                "executive_risk_drivers"
            ],

            "executive_risk_interpretation":
            executive_risk[
                "executive_risk_interpretation"
            ],

            "status": "ok"
        }

    except Exception as error:

        return {

            "ticker": ticker.upper(),

            "company": ticker.upper(),

            "quiet_signal_level": "Unavailable",

            "severity_rank": 0,

            "status": "error",

            "error":
            str(error)
        }


def generate_market_brief(
    tickers=None
):

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    tickers_to_review = (
        tickers or DEFAULT_BRIEF_TICKERS
    )

    company_briefs = [

        _safe_get_company_intelligence(
            ticker
        )

        for ticker in tickers_to_review
    ]

    ranked_company_briefs = sorted(

        company_briefs,

        key=lambda item:

        item.get(
            "executive_risk_score",
            0
        ),

        reverse=True
    )

    top_risk = (

        ranked_company_briefs[0]

        if ranked_company_briefs

        else None
    )

    return {

        "generated_at":
        current_time,

        "brief_type":
        "CounselIQ Morning Intelligence Brief",

        "version":
        "0.3.0",

        "tickers_reviewed":

        [
            ticker.upper()

            for ticker in tickers_to_review
        ],

        "top_executive_risk":
        top_risk,

        "ranked_company_briefs":
        ranked_company_briefs,

        "counseliq_summary":

        (
            "CounselIQ now ranks companies using "
            "Executive Risk Severity scoring "
            "across filing changes, "
            "leadership signals, "
            "and quiet-signal behavior."
        )
    }