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


RISK_KEYWORDS = [
    "risk",
    "uncertainty",
    "decline",
    "decrease",
    "adverse",
    "material adverse",
    "weakness",
    "litigation",
    "regulatory",
    "investigation",
    "impairment",
    "disruption",
    "supply chain",
    "competition",
    "macroeconomic",
]


CONFIDENCE_KEYWORDS = [
    "strong demand",
    "continued growth",
    "expects",
    "believes",
    "confident",
    "favorable",
    "opportunity",
    "momentum",
    "growth",
    "innovation",
    "expanded",
    "improved",
]


LIQUIDITY_DEBT_KEYWORDS = [
    "liquidity",
    "debt",
    "borrowings",
    "credit facility",
    "refinancing",
    "cash flow",
    "capital resources",
    "convertible",
    "notes payable",
    "going concern",
]


CAPITAL_ALLOCATION_KEYWORDS = [
    "repurchase",
    "share repurchase",
    "dividend",
    "capital return",
    "shareholder return",
    "marketable securities",
    "cash equivalents",
    "debt securities",
]


COMPARABLE_FORMS = ["10-Q", "10-K"]


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


def get_recent_sec_filings(cik: str, limit: int = 80):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=SEC_HEADERS, timeout=10)
    response.raise_for_status()

    data = response.json()
    recent = data.get("filings", {}).get("recent", {})

    filings = []

    total_available = len(recent.get("form", []))

    for i in range(min(limit, total_available)):
        filings.append({
            "form": recent["form"][i],
            "filing_date": recent["filingDate"][i],
            "report_date": recent["reportDate"][i],
            "accession_number": recent["accessionNumber"][i],
            "primary_document": recent["primaryDocument"][i],
        })

    return filings


def get_comparable_periodic_filings(filings: list):
    comparable = []

    for filing in filings:
        if filing.get("form") in COMPARABLE_FORMS:
            comparable.append(filing)

    return comparable


def choose_best_filing_for_analysis(filings: list):
    comparable_filings = get_comparable_periodic_filings(filings)

    if comparable_filings:
        return comparable_filings[0]

    preferred_forms = ["8-K", "S-3", "S-1", "424B", "4", "144"]

    for preferred_form in preferred_forms:
        for filing in filings:
            if filing.get("form") == preferred_form:
                return filing

    return filings[0] if filings else None


def choose_previous_comparable_filing(filings: list, selected_filing: dict):
    if not selected_filing:
        return None

    selected_form = selected_filing.get("form")
    selected_accession = selected_filing.get("accession_number")

    comparable_filings = [
        filing for filing in filings
        if filing.get("form") == selected_form
    ]

    for filing in comparable_filings:
        if filing.get("accession_number") != selected_accession:
            return filing

    return None


def build_filing_document_url(cik_no_leading_zeroes: str, filing: dict):
    accession_clean = filing["accession_number"].replace("-", "")
    primary_document = filing["primary_document"]

    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_leading_zeroes}/{accession_clean}/{primary_document}"
    )


def get_filing_document_text(cik_no_leading_zeroes: str, filing: dict):
    document_url = build_filing_document_url(cik_no_leading_zeroes, filing)

    response = requests.get(document_url, headers=SEC_HEADERS, timeout=20)
    response.raise_for_status()

    raw_text = response.text
    cleaned_text = clean_filing_text(raw_text)
    cleaned_preview = extract_text_preview(cleaned_text, max_length=3000)
    key_sections = extract_key_sections(cleaned_text)
    narrative_chunks = extract_narrative_chunks(cleaned_text, max_chunks=15)

    return {
        "document_url": document_url,
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "raw_text_length": len(raw_text),
        "cleaned_text_length": len(cleaned_text),
        "cleaned_text_preview": cleaned_preview,
        "key_sections": key_sections,
        "narrative_chunks": narrative_chunks,
    }


def count_keyword_hits(text: str, keywords: list):
    lower_text = text.lower()
    total = 0

    for keyword in keywords:
        total += lower_text.count(keyword.lower())

    return total


def detect_new_keywords(current_text: str, previous_text: str, keywords: list):
    current_lower = current_text.lower()
    previous_lower = previous_text.lower()

    new_terms = []

    for keyword in keywords:
        if keyword.lower() in current_lower and keyword.lower() not in previous_lower:
            new_terms.append(keyword)

    return new_terms


def build_filing_comparison(current_filing_data: dict, previous_filing_data: dict):
    if not current_filing_data or not previous_filing_data:
        return {
            "comparison_available": False,
            "summary": "Prior comparable filing was not available for comparison.",
            "tone_shift": "Unavailable",
            "new_risk_terms": [],
            "new_liquidity_debt_terms": [],
            "new_capital_allocation_terms": [],
            "confidence_language_change": "Unavailable",
            "risk_language_change": "Unavailable",
            "liquidity_debt_language_change": "Unavailable",
            "capital_allocation_language_change": "Unavailable",
        }

    current_text = current_filing_data["cleaned_text"]
    previous_text = previous_filing_data["cleaned_text"]

    current_risk_count = count_keyword_hits(current_text, RISK_KEYWORDS)
    previous_risk_count = count_keyword_hits(previous_text, RISK_KEYWORDS)

    current_confidence_count = count_keyword_hits(current_text, CONFIDENCE_KEYWORDS)
    previous_confidence_count = count_keyword_hits(previous_text, CONFIDENCE_KEYWORDS)

    current_liquidity_debt_count = count_keyword_hits(current_text, LIQUIDITY_DEBT_KEYWORDS)
    previous_liquidity_debt_count = count_keyword_hits(previous_text, LIQUIDITY_DEBT_KEYWORDS)

    current_capital_allocation_count = count_keyword_hits(current_text, CAPITAL_ALLOCATION_KEYWORDS)
    previous_capital_allocation_count = count_keyword_hits(previous_text, CAPITAL_ALLOCATION_KEYWORDS)

    new_risk_terms = detect_new_keywords(current_text, previous_text, RISK_KEYWORDS)
    new_liquidity_debt_terms = detect_new_keywords(current_text, previous_text, LIQUIDITY_DEBT_KEYWORDS)
    new_capital_allocation_terms = detect_new_keywords(current_text, previous_text, CAPITAL_ALLOCATION_KEYWORDS)

    risk_delta = current_risk_count - previous_risk_count
    confidence_delta = current_confidence_count - previous_confidence_count
    liquidity_debt_delta = current_liquidity_debt_count - previous_liquidity_debt_count
    capital_allocation_delta = current_capital_allocation_count - previous_capital_allocation_count

    if risk_delta > 20 or liquidity_debt_delta > 10:
        tone_shift = "More defensive"
    elif confidence_delta > 10 and risk_delta <= 0:
        tone_shift = "More confident"
    elif abs(risk_delta) <= 10 and abs(confidence_delta) <= 10:
        tone_shift = "Stable"
    else:
        tone_shift = "Mixed"

    summary = (
        f"Compared latest {current_filing_data.get('form', 'filing')} against the prior comparable filing. "
        f"Risk language changed by {risk_delta} references, confidence language changed by "
        f"{confidence_delta} references, liquidity/debt language changed by {liquidity_debt_delta} "
        f"references, and capital allocation language changed by {capital_allocation_delta} references."
    )

    return {
        "comparison_available": True,
        "summary": summary,
        "tone_shift": tone_shift,
        "new_risk_terms": new_risk_terms,
        "new_liquidity_debt_terms": new_liquidity_debt_terms,
        "new_capital_allocation_terms": new_capital_allocation_terms,
        "current_risk_count": current_risk_count,
        "previous_risk_count": previous_risk_count,
        "risk_language_delta": risk_delta,
        "current_confidence_count": current_confidence_count,
        "previous_confidence_count": previous_confidence_count,
        "confidence_language_delta": confidence_delta,
        "current_liquidity_debt_count": current_liquidity_debt_count,
        "previous_liquidity_debt_count": previous_liquidity_debt_count,
        "liquidity_debt_language_delta": liquidity_debt_delta,
        "current_capital_allocation_count": current_capital_allocation_count,
        "previous_capital_allocation_count": previous_capital_allocation_count,
        "capital_allocation_language_delta": capital_allocation_delta,
        "confidence_language_change": (
            "Increased" if confidence_delta > 0 else "Decreased" if confidence_delta < 0 else "Stable"
        ),
        "risk_language_change": (
            "Increased" if risk_delta > 0 else "Decreased" if risk_delta < 0 else "Stable"
        ),
        "liquidity_debt_language_change": (
            "Increased" if liquidity_debt_delta > 0 else "Decreased" if liquidity_debt_delta < 0 else "Stable"
        ),
        "capital_allocation_language_change": (
            "Increased" if capital_allocation_delta > 0 else "Decreased" if capital_allocation_delta < 0 else "Stable"
        ),
    }


def build_notable_changes(filing_comparison: dict):
    if not filing_comparison or not filing_comparison.get("comparison_available"):
        return []

    changes = []

    if filing_comparison["risk_language_delta"] > 0:
        changes.append(
            f"Risk language increased by {filing_comparison['risk_language_delta']} references versus the prior comparable filing."
        )

    if filing_comparison["risk_language_delta"] < 0:
        changes.append(
            f"Risk language decreased by {abs(filing_comparison['risk_language_delta'])} references versus the prior comparable filing."
        )

    if filing_comparison["confidence_language_delta"] > 0:
        changes.append(
            f"Confidence/growth language increased by {filing_comparison['confidence_language_delta']} references."
        )

    if filing_comparison["confidence_language_delta"] < 0:
        changes.append(
            f"Confidence/growth language decreased by {abs(filing_comparison['confidence_language_delta'])} references."
        )

    if filing_comparison["liquidity_debt_language_delta"] > 0:
        changes.append(
            f"Liquidity/debt language increased by {filing_comparison['liquidity_debt_language_delta']} references."
        )

    if filing_comparison["liquidity_debt_language_delta"] < 0:
        changes.append(
            f"Liquidity/debt language decreased by {abs(filing_comparison['liquidity_debt_language_delta'])} references."
        )

    if filing_comparison["new_risk_terms"]:
        changes.append(
            "New risk-related terms detected: "
            + ", ".join(filing_comparison["new_risk_terms"])
        )

    if filing_comparison["new_liquidity_debt_terms"]:
        changes.append(
            "New liquidity/debt terms detected: "
            + ", ".join(filing_comparison["new_liquidity_debt_terms"])
        )

    if not changes:
        changes.append("No major filing-language changes detected versus the prior comparable filing.")

    return changes


def get_sec_filing_summary(ticker: str):
    company = get_cik_for_ticker(ticker)

    if company is None:
        return {
            "ticker": ticker.upper(),
            "company_name": None,
            "cik": None,
            "latest_filings_reviewed": [],
            "selected_filing": None,
            "previous_comparable_filing": None,
            "selected_filing_text_preview": None,
            "selected_filing_url": None,
            "previous_filing_url": None,
            "selected_filing_text_length": 0,
            "selected_filing_cleaned_text_length": 0,
            "key_sections": {},
            "narrative_chunks": [],
            "filing_summary": "Ticker not found in SEC company ticker mapping.",
            "notable_changes": [],
            "risk_flags": ["Ticker lookup failed"],
            "filing_comparison": {
                "comparison_available": False,
                "summary": "Ticker lookup failed.",
            },
        }

    filings = get_recent_sec_filings(company["cik"], limit=80)
    selected_filing = choose_best_filing_for_analysis(filings)
    previous_comparable_filing = choose_previous_comparable_filing(
        filings,
        selected_filing,
    )

    filing_text_data = None
    previous_filing_text_data = None

    if selected_filing:
        filing_text_data = get_filing_document_text(
            company["cik_no_leading_zeroes"],
            selected_filing,
        )

        filing_text_data["form"] = selected_filing.get("form")
        filing_text_data["filing_date"] = selected_filing.get("filing_date")

    if previous_comparable_filing:
        previous_filing_text_data = get_filing_document_text(
            company["cik_no_leading_zeroes"],
            previous_comparable_filing,
        )

        previous_filing_text_data["form"] = previous_comparable_filing.get("form")
        previous_filing_text_data["filing_date"] = previous_comparable_filing.get("filing_date")

    filing_comparison = build_filing_comparison(
        filing_text_data,
        previous_filing_text_data,
    )

    notable_changes = build_notable_changes(filing_comparison)

    return {
        "ticker": company["ticker"],
        "company_name": company["company_name"],
        "cik": company["cik"],
        "latest_filings_reviewed": filings[:10],
        "selected_filing": selected_filing,
        "previous_comparable_filing": previous_comparable_filing,
        "selected_filing_url": filing_text_data["document_url"] if filing_text_data else None,
        "previous_filing_url": previous_filing_text_data["document_url"] if previous_filing_text_data else None,
        "selected_filing_text_preview": filing_text_data["cleaned_text_preview"] if filing_text_data else None,
        "selected_filing_text_length": filing_text_data["raw_text_length"] if filing_text_data else 0,
        "selected_filing_cleaned_text_length": filing_text_data["cleaned_text_length"] if filing_text_data else 0,
        "key_sections": filing_text_data["key_sections"] if filing_text_data else {},
        "narrative_chunks": filing_text_data["narrative_chunks"] if filing_text_data else [],
        "filing_summary": f"Retrieved {len(filings[:10])} recent SEC filings for {company['company_name']}.",
        "notable_changes": notable_changes,
        "risk_flags": [],
        "filing_comparison": filing_comparison,
    }