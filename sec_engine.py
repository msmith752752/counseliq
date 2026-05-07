import requests

from filing_parser import (
    clean_filing_text,
    extract_text_preview,
    extract_key_sections,
    extract_narrative_chunks,
)


SEC_HEADERS = {
    "User-Agent": "CounselIQ contact@example.com"
}


def get_cik_for_ticker(ticker: str):
    ticker = ticker.upper()

    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=10)
    response.raise_for_status()

    companies = response.json()

    for company in companies.values():
        if company["ticker"].upper() == ticker:
            cik = str(company["cik_str"]).zfill(10)
            return {
                "ticker": company["ticker"],
                "company_name": company["title"],
                "cik": cik,
                "cik_no_leading_zeroes": str(company["cik_str"]),
            }

    return None


def get_recent_sec_filings(cik: str, limit: int = 10):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=10)
    response.raise_for_status()

    data = response.json()
    recent = data.get("filings", {}).get("recent", {})

    filings = []

    for i in range(min(limit, len(recent.get("form", [])))):
        filings.append({
            "form": recent["form"][i],
            "filing_date": recent["filingDate"][i],
            "report_date": recent["reportDate"][i],
            "accession_number": recent["accessionNumber"][i],
            "primary_document": recent["primaryDocument"][i],
        })

    return filings


def choose_best_filing_for_analysis(filings: list):
    preferred_forms = ["10-Q", "10-K", "8-K"]

    for preferred_form in preferred_forms:
        for filing in filings:
            if filing["form"] == preferred_form:
                return filing

    return filings[0] if filings else None


def build_filing_document_url(cik_no_leading_zeroes: str, filing: dict):
    accession_clean = filing["accession_number"].replace("-", "")
    primary_document = filing["primary_document"]

    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_leading_zeroes}/{accession_clean}/{primary_document}"
    )


def get_filing_document_text(cik_no_leading_zeroes: str, filing: dict):
    document_url = build_filing_document_url(cik_no_leading_zeroes, filing)

    response = requests.get(document_url, headers=SEC_HEADERS, timeout=15)
    response.raise_for_status()

    raw_text = response.text
    cleaned_text = clean_filing_text(raw_text)
    cleaned_preview = extract_text_preview(cleaned_text, max_length=3000)
    key_sections = extract_key_sections(cleaned_text)
    narrative_chunks = extract_narrative_chunks(cleaned_text, max_chunks=15)

    return {
        "document_url": document_url,
        "raw_text_length": len(raw_text),
        "cleaned_text_length": len(cleaned_text),
        "cleaned_text_preview": cleaned_preview,
        "key_sections": key_sections,
        "narrative_chunks": narrative_chunks,
    }


def get_sec_filing_summary(ticker: str):
    company = get_cik_for_ticker(ticker)

    if company is None:
        return {
            "ticker": ticker.upper(),
            "company_name": None,
            "cik": None,
            "latest_filings_reviewed": [],
            "selected_filing": None,
            "selected_filing_text_preview": None,
            "selected_filing_url": None,
            "selected_filing_text_length": 0,
            "selected_filing_cleaned_text_length": 0,
            "key_sections": {},
            "narrative_chunks": [],
            "filing_summary": "Ticker not found in SEC company ticker mapping.",
            "notable_changes": [],
            "risk_flags": ["Ticker lookup failed"],
        }

    filings = get_recent_sec_filings(company["cik"], limit=10)
    selected_filing = choose_best_filing_for_analysis(filings)

    filing_text_data = None

    if selected_filing:
        filing_text_data = get_filing_document_text(
            company["cik_no_leading_zeroes"],
            selected_filing,
        )

    return {
        "ticker": company["ticker"],
        "company_name": company["company_name"],
        "cik": company["cik"],
        "latest_filings_reviewed": filings,
        "selected_filing": selected_filing,
        "selected_filing_url": filing_text_data["document_url"] if filing_text_data else None,
        "selected_filing_text_preview": filing_text_data["cleaned_text_preview"] if filing_text_data else None,
        "selected_filing_text_length": filing_text_data["raw_text_length"] if filing_text_data else 0,
        "selected_filing_cleaned_text_length": filing_text_data["cleaned_text_length"] if filing_text_data else 0,
        "key_sections": filing_text_data["key_sections"] if filing_text_data else {},
        "narrative_chunks": filing_text_data["narrative_chunks"] if filing_text_data else [],
        "filing_summary": f"Retrieved {len(filings)} recent SEC filings for {company['company_name']}.",
        "notable_changes": [],
        "risk_flags": [],
    }