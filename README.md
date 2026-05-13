# CounselIQ

CounselIQ is a corporate behavioral intelligence platform designed to surface hidden leadership, filing, and narrative shifts that may affect public companies before they become obvious in headlines or price action.

The goal is not to be a stock screener, charting platform, or AI stock picker. CounselIQ focuses on executive behavior, SEC disclosure changes, risk language, strategic tone, and quiet signals that may help investors understand what is changing beneath the surface.

## Core Concept

Markets often move because expectations, uncertainty, confidence, and leadership behavior change.

CounselIQ analyzes public company filings and executive language to identify signals such as:

- Defensive language increasing
- Regulatory or legal exposure emerging
- Business disruption language
- Mixed management signals
- Liquidity or debt pressure
- Capital allocation shifts
- Strategic uncertainty increasing

## Current Features

### SEC Filing Intelligence

CounselIQ retrieves and analyzes recent SEC filings, including comparable filing selection for quarter-over-quarter review.

### Executive Intelligence Brief

For a selected ticker, CounselIQ generates an executive-style brief that includes:

- Executive summary
- Leadership signal score
- Leadership signal label
- Leadership tone
- Strategic focus
- Capital allocation interpretation
- Risk themes
- CounselIQ interpretation

### Filing Comparison Engine

CounselIQ compares the latest filing against a prior comparable filing and detects changes in:

- Risk language
- Confidence/growth language
- Liquidity/debt language
- Capital allocation language
- Newly introduced risk terms

### Quiet Signals Engine

The Quiet Signals Engine identifies hidden corporate signals and assigns a quiet signal level such as Calm, Moderate, or Elevated.

### Market Brief Engine

The `/market-brief` endpoint reviews a default multi-company watchlist, pulls real company intelligence, ranks quiet signals, and highlights the highest-risk narrative shifts first.

Current default watchlist:

- AAPL
- NVDA
- MSFT
- JPM
- AMZN

## Current API Endpoints

### Health Check

```text
GET /



Returns basic backend status.

Company Brief
GET /brief/{ticker}

Example:

http://127.0.0.1:8000/brief/AAPL

Returns a detailed company-level CounselIQ intelligence brief.

Market Brief
GET /market-brief

Example:

http://127.0.0.1:8000/market-brief

Returns a multi-company morning intelligence brief ranked by quiet signal severity.

Project Structure
backend/
├── main.py
├── sec_engine.py
├── ai_engine.py
├── quiet_signals_engine.py
├── market_brief_engine.py
├── dashboard.html
└── requirements.txt
Backend Architecture
SEC Filing
→ Cleanup
→ Narrative Extraction
→ Theme Detection
→ Filing Comparison
→ Executive Interpretation
→ Quiet Signals Engine
→ Market Brief Engine
→ Dashboard Intelligence
Running Locally

From the backend folder:

C:\Users\msmit\counseliq\backend>

Activate the virtual environment:

venv\Scripts\activate

Expected prompt:

(venv) C:\Users\msmit\counseliq\backend>

Run the FastAPI backend:

python -m uvicorn main:app --reload

Then open:

http://127.0.0.1:8000/
Product Direction

CounselIQ is evolving into a:

Corporate Behavioral Intelligence Engine

The long-term goal is to help users open the platform each morning and quickly understand what changed behind the scenes across public companies.

Future planned intelligence layers include:

Executive Risk Severity Score
Quiet signal weighting/history
Earnings transcript ingestion
Insider activity engine
Multi-quarter trend tracking
Options volatility interpretation layer
Historical signal accuracy tracking
Leadership credibility scoring
Litigation detection
Guidance shift intelligence
Futures, VIX, rates, and earnings calendar integration
Design Philosophy

CounselIQ should feel like an institutional intelligence terminal.

It should not look or behave like:

A retail stock screener
A charting platform
A technical analysis dashboard
An AI stock picker

It should emphasize:

Signal hierarchy
Narrative change detection
Executive behavior
Filing delta intelligence
Institutional-style interpretation
Clear risk prioritization
Disclaimer

CounselIQ is an educational and research tool. It does not provide financial advice, investment recommendations, or trading instructions. Users should conduct their own research and consult qualified professionals before making investment decisions.
