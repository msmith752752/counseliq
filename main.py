from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sec_engine import get_sec_filing_summary
from ai_engine import generate_executive_brief
from quiet_signals_engine import build_quiet_signals

app = FastAPI(
    title="CounselIQ API",
    description="Executive intelligence platform for SEC filings, leadership signals, and corporate strategy.",
    version="0.3.0",
)

# Allow local dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "app": "CounselIQ",
        "status": "running",
        "message": "CounselIQ backend is live.",
    }


@app.get("/brief/{ticker}")
def get_company_brief(ticker: str):

    # Retrieve SEC filing intelligence
    sec_data = get_sec_filing_summary(ticker)

    # Generate executive intelligence layer
    ai_brief = generate_executive_brief(ticker, sec_data)

    # Generate behind-the-scenes quiet signal intelligence
    quiet_signal_data = build_quiet_signals(ticker, sec_data, ai_brief)

    return {
        "ticker": ticker.upper(),

        # Executive intelligence
        "executive_summary": ai_brief["executive_summary"],
        "leadership_signal_score": ai_brief["leadership_signal_score"],
        "leadership_signal_label": ai_brief["leadership_signal_label"],
        "leadership_signal_explanation": ai_brief["leadership_signal_explanation"],
        "leadership_tone": ai_brief["leadership_tone"],
        "strategic_focus": ai_brief["strategic_focus"],
        "capital_allocation": ai_brief["capital_allocation"],
        "risk_themes": ai_brief["risk_themes"],
        "counseliq_interpretation": ai_brief["counseliq_interpretation"],

        # Quiet Signals Engine
        "quiet_signal_level": quiet_signal_data["quiet_signal_level"],
        "quiet_signal_summary": quiet_signal_data["quiet_signal_summary"],
        "quiet_signals": quiet_signal_data["quiet_signals"],

        # SEC filing intelligence
        "sec_summary": sec_data["filing_summary"],
        "latest_filings_reviewed": sec_data["latest_filings_reviewed"],
        "selected_filing": sec_data["selected_filing"],
        "selected_filing_url": sec_data["selected_filing_url"],
        "selected_filing_text_length": sec_data["selected_filing_text_length"],
        "selected_filing_cleaned_text_length": sec_data["selected_filing_cleaned_text_length"],
        "selected_filing_text_preview": sec_data["selected_filing_text_preview"],

        # Filing comparison engine
        "previous_comparable_filing": sec_data["previous_comparable_filing"],
        "previous_filing_url": sec_data["previous_filing_url"],
        "filing_comparison": sec_data["filing_comparison"],
        "filing_changes": sec_data["notable_changes"],

        # Additional analysis
        "risk_signals": sec_data["risk_flags"],
        "key_sections": sec_data["key_sections"],
        "narrative_chunks": sec_data["narrative_chunks"],

        # Future intelligence modules
        "insider_activity": "Pending insider analysis.",
    }