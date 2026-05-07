from bs4 import BeautifulSoup
import re


def clean_filing_text(raw_html: str):
    """
    Convert SEC filing HTML/XBRL into cleaner readable text.
    """

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n+", "\n", text)

    # Remove common XBRL/accounting taxonomy noise
    text = re.sub(r"\b[a-zA-Z]+-[a-zA-Z]+:[A-Za-z0-9]+", " ", text)
    text = re.sub(r"\b[a-zA-Z]+:[A-Za-z0-9]+", " ", text)
    text = re.sub(r"http[s]?://\S+", " ", text)

    return text.strip()


def find_meaningful_start(cleaned_text: str):

    start_patterns = [
        "PART I",
        "Management’s Discussion and Analysis",
        "Management's Discussion and Analysis",
        "Risk Factors",
    ]

    lower_text = cleaned_text.lower()

    for pattern in start_patterns:
        index = lower_text.find(pattern.lower())

        if index != -1:
            return index

    return 0


def extract_text_preview(cleaned_text: str, max_length: int = 3000):

    start_index = find_meaningful_start(cleaned_text)

    preview = cleaned_text[start_index:start_index + max_length]

    return preview.strip()


def split_into_chunks(text: str):
    """
    Split filing into paragraph-style chunks.
    """

    raw_chunks = text.split("\n")

    cleaned_chunks = []

    for chunk in raw_chunks:

        chunk = chunk.strip()

        if len(chunk) < 40:
            continue

        cleaned_chunks.append(chunk)

    return cleaned_chunks


def is_narrative_chunk(chunk: str):
    """
    Score whether a chunk appears narrative/prose-heavy.
    """

    words = chunk.split()

    if len(words) < 12:
        return False

    digit_count = sum(c.isdigit() for c in chunk)

    # Too numeric
    if digit_count > len(chunk) * 0.25:
        return False

    # Mostly symbols/numbers
    if re.fullmatch(r"[\d\$\%\-\(\)\s\,\.]+", chunk):
        return False

    narrative_keywords = [
        "company",
        "management",
        "operations",
        "business",
        "market",
        "customers",
        "services",
        "products",
        "growth",
        "strategy",
        "financial",
        "results",
        "expects",
        "believes",
        "risk",
    ]

    keyword_hits = 0

    lower_chunk = chunk.lower()

    for keyword in narrative_keywords:
        if keyword in lower_chunk:
            keyword_hits += 1

    return keyword_hits >= 2


def extract_narrative_chunks(cleaned_text: str, max_chunks: int = 15):
    """
    Extract narrative/prose-heavy chunks from filing.
    """

    chunks = split_into_chunks(cleaned_text)

    narrative_chunks = []

    for chunk in chunks:

        if is_narrative_chunk(chunk):
            narrative_chunks.append(chunk)

        if len(narrative_chunks) >= max_chunks:
            break

    return narrative_chunks


def extract_key_sections(cleaned_text: str):
    """
    Placeholder structured sections.
    """

    return {
        "management_discussion": None,
        "risk_factors": None,
        "legal_proceedings": None,
        "financial_statements": None,
    }