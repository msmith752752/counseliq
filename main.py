from fastapi import FastAPI
from sec_engine import get_sec_filing_summary
from ai_engine import generate_executive_brief

app = FastAPI(
    title="CounselIQ API",
    description="Executive intelligence platform for SEC filings, leadership signals, and corporate strategy.",
    version="0.1.0",
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

    # Retrieve SEC filing data
    sec_data = get_sec_filing_summary(ticker)

    # Generate intelligence brief
    ai_brief = generate_executive_brief(ticker, sec_data)

    return {
        "ticker": ticker.upper(),
        "executive_summary": ai_brief["executive_summary"],
        "leadership_signal_score": ai_brief["leadership_signal_score"],
        "leadership_signal_label": ai_brief["leadership_signal_label"],
        "leadership_signal_explanation": ai_brief["leadership_signal_explanation"],
        "leadership_tone": ai_brief["leadership_tone"],
        "strategic_focus": ai_brief["strategic_focus"],
        "risk_signals": sec_data["risk_flags"],
        "risk_themes": ai_brief["risk_themes"],
        "capital_allocation": ai_brief["capital_allocation"],
        "filing_changes": sec_data["notable_changes"],
        "insider_activity": "Pending insider analysis.",
        "sec_summary": sec_data["filing_summary"],
        "latest_filings_reviewed": sec_data["latest_filings_reviewed"],
        "selected_filing": sec_data["selected_filing"],
        "selected_filing_url": sec_data["selected_filing_url"],
        "selected_filing_text_length": sec_data["selected_filing_text_length"],
        "selected_filing_cleaned_text_length": sec_data["selected_filing_cleaned_text_length"],
        "selected_filing_text_preview": sec_data["selected_filing_text_preview"],
        "key_sections": sec_data["key_sections"],
        "narrative_chunks": sec_data["narrative_chunks"],
        "counseliq_interpretation": ai_brief["counseliq_interpretation"],
    }