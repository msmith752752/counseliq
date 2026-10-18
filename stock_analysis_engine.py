import yfinance as yf
from datetime import datetime


def _safe(val, default=None):
    try:
        if val is None:
            return default
        import math
        if isinstance(val, float) and math.isnan(val):
            return default
        return val
    except Exception:
        return default


def _fmt_large(val):
    try:
        val = float(val)
        if val >= 1_000_000_000:
            return f"${val / 1_000_000_000:.2f}B"
        elif val >= 1_000_000:
            return f"${val / 1_000_000:.2f}M"
        else:
            return f"${val:,.0f}"
    except Exception:
        return "N/A"


def _pct(val):
    try:
        return f"{float(val) * 100:.1f}%"
    except Exception:
        return "N/A"


def build_stock_analysis(ticker: str) -> dict:
    ticker = ticker.upper()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}
    except Exception as e:
        return {
            "ticker": ticker,
            "status": "error",
            "error": f"Could not retrieve data for {ticker}: {str(e)}",
        }

    # Company Profile
    company_name     = _safe(info.get("longName") or info.get("shortName"), ticker)
    sector           = _safe(info.get("sector"), "N/A")
    industry         = _safe(info.get("industry"), "N/A")
    business_summary = _safe(info.get("longBusinessSummary"), "No description available.")
    website          = _safe(info.get("website"), "N/A")
    employees        = _safe(info.get("fullTimeEmployees"))
    country          = _safe(info.get("country"), "N/A")

    # Price & Market Data
    current_price  = _safe(info.get("currentPrice") or info.get("regularMarketPrice"))
    previous_close = _safe(info.get("previousClose"))
    open_price     = _safe(info.get("open"))
    day_high       = _safe(info.get("dayHigh"))
    day_low        = _safe(info.get("dayLow"))
    week_52_high   = _safe(info.get("fiftyTwoWeekHigh"))
    week_52_low    = _safe(info.get("fiftyTwoWeekLow"))
    volume         = _safe(info.get("volume"))
    avg_volume     = _safe(info.get("averageVolume"))
    market_cap     = _safe(info.get("marketCap"))
    beta           = _safe(info.get("beta"))

    price_change     = None
    price_change_pct = None
    if current_price and previous_close:
        try:
            price_change     = round(current_price - previous_close, 2)
            price_change_pct = round((price_change / previous_close) * 100, 2)
        except Exception:
            pass

    week_52_position = None
    if week_52_high and week_52_low and current_price:
        try:
            rng = week_52_high - week_52_low
            if rng > 0:
                week_52_position = round(((current_price - week_52_low) / rng) * 100, 1)
        except Exception:
            pass

    volume_vs_avg = None
    if volume and avg_volume and avg_volume > 0:
        try:
            volume_vs_avg = round((volume / avg_volume) * 100, 1)
        except Exception:
            pass

    # Valuation
    pe_ratio      = _safe(info.get("trailingPE"))
    forward_pe    = _safe(info.get("forwardPE"))
    peg_ratio     = _safe(info.get("pegRatio"))
    price_to_book = _safe(info.get("priceToBook"))
    price_to_sales= _safe(info.get("priceToSalesTrailing12Months"))
    ev_to_ebitda  = _safe(info.get("enterpriseToEbitda"))
    ev_to_revenue = _safe(info.get("enterpriseToRevenue"))

    # Earnings & Revenue
    eps_ttm           = _safe(info.get("trailingEps"))
    eps_forward       = _safe(info.get("forwardEps"))
    revenue_ttm       = _safe(info.get("totalRevenue"))
    gross_margins     = _safe(info.get("grossMargins"))
    operating_margins = _safe(info.get("operatingMargins"))
    profit_margins    = _safe(info.get("profitMargins"))
    revenue_growth    = _safe(info.get("revenueGrowth"))
    earnings_growth   = _safe(info.get("earningsGrowth"))
    earnings_date     = None

    try:
        cal = stock.calendar
        if cal is not None:
            if hasattr(cal, 'get'):
                ed = cal.get("Earnings Date")
                if ed is not None:
                    if hasattr(ed, '__iter__') and not isinstance(ed, str):
                        ed_list = list(ed)
                        if ed_list:
                            earnings_date = str(ed_list[0])
                    else:
                        earnings_date = str(ed)
            elif hasattr(cal, 'iloc'):
                if 'Earnings Date' in cal.columns:
                    earnings_date = str(cal['Earnings Date'].iloc[0])
    except Exception:
        pass

    # Balance Sheet
    total_cash       = _safe(info.get("totalCash"))
    total_debt       = _safe(info.get("totalDebt"))
    debt_to_equity   = _safe(info.get("debtToEquity"))
    current_ratio    = _safe(info.get("currentRatio"))
    quick_ratio      = _safe(info.get("quickRatio"))
    free_cash_flow   = _safe(info.get("freeCashflow"))
    return_on_equity = _safe(info.get("returnOnEquity"))
    return_on_assets = _safe(info.get("returnOnAssets"))

    # Analyst
    analyst_target = _safe(info.get("targetMeanPrice"))
    analyst_high   = _safe(info.get("targetHighPrice"))
    analyst_low    = _safe(info.get("targetLowPrice"))
    analyst_count  = _safe(info.get("numberOfAnalystOpinions"))
    recommendation = _safe(info.get("recommendationKey"), "N/A").replace("_", " ").title()

    upside_to_target = None
    if analyst_target and current_price and current_price > 0:
        try:
            upside_to_target = round(((analyst_target - current_price) / current_price) * 100, 1)
        except Exception:
            pass

    # Dividend
    dividend_rate  = _safe(info.get("dividendRate"))
    dividend_yield = _safe(info.get("dividendYield"))
    payout_ratio   = _safe(info.get("payoutRatio"))

    # News
    news_items = []
    try:
        raw_news = stock.news or []
        for item in raw_news[:6]:
            content = item.get("content", {})
            title   = content.get("title") or item.get("title", "")
            summary = content.get("summary") or ""
            pub_raw = content.get("pubDate") or item.get("providerPublishTime", "")
            source  = ""
            try:
                provider = content.get("provider", {})
                source = provider.get("displayName", "") if isinstance(provider, dict) else ""
            except Exception:
                pass
            url = ""
            try:
                canon = content.get("canonicalUrl", {})
                url = canon.get("url", "") if isinstance(canon, dict) else ""
                if not url:
                    url = item.get("link", "")
            except Exception:
                url = item.get("link", "")

            if title:
                news_items.append({
                    "title":     title,
                    "summary":   summary[:200] if summary else "",
                    "source":    source,
                    "published": str(pub_raw),
                    "url":       url,
                })
    except Exception:
        pass

    # CounselIQ Signals
    signals = []

    if week_52_position is not None:
        if week_52_position <= 15:
            signals.append({
                "signal": "Near 52-Week Low",
                "type": "price",
                "severity": "Watch",
                "detail": f"Stock is trading in the bottom {week_52_position:.0f}% of its 52-week range."
            })
        elif week_52_position >= 85:
            signals.append({
                "signal": "Near 52-Week High",
                "type": "price",
                "severity": "Note",
                "detail": f"Stock is trading in the top {100 - week_52_position:.0f}% of its 52-week range."
            })

    if pe_ratio and pe_ratio > 50:
        signals.append({
            "signal": "Elevated Valuation",
            "type": "valuation",
            "severity": "Watch",
            "detail": f"Trailing P/E of {pe_ratio:.1f}x is elevated. Growth must continue to justify current pricing."
        })
    elif pe_ratio and pe_ratio < 10:
        signals.append({
            "signal": "Low Valuation",
            "type": "valuation",
            "severity": "Note",
            "detail": f"Trailing P/E of {pe_ratio:.1f}x is low. May signal value or declining growth expectations."
        })

    if upside_to_target is not None:
        if upside_to_target >= 30:
            signals.append({
                "signal": "Significant Analyst Upside",
                "type": "analyst",
                "severity": "Positive",
                "detail": f"Analyst consensus target implies {upside_to_target:.1f}% upside from current price."
            })
        elif upside_to_target <= -15:
            signals.append({
                "signal": "Trading Above Analyst Target",
                "type": "analyst",
                "severity": "Watch",
                "detail": f"Stock is {abs(upside_to_target):.1f}% above analyst consensus target."
            })

    if volume_vs_avg is not None and volume_vs_avg >= 200:
        signals.append({
            "signal": "Elevated Volume",
            "type": "market",
            "severity": "Watch",
            "detail": f"Today's volume is {volume_vs_avg:.0f}% of average — significantly elevated activity."
        })

    if debt_to_equity is not None and debt_to_equity > 200:
        signals.append({
            "signal": "High Debt Load",
            "type": "balance_sheet",
            "severity": "Watch",
            "detail": f"Debt-to-equity of {debt_to_equity:.0f}% suggests significant leverage."
        })

    if profit_margins is not None and profit_margins < 0:
        signals.append({
            "signal": "Negative Profit Margins",
            "type": "financials",
            "severity": "Watch",
            "detail": f"Company is currently unprofitable with profit margin of {_pct(profit_margins)}."
        })

    if not signals:
        signals.append({
            "signal": "No Major Market Signals",
            "type": "baseline",
            "severity": "Neutral",
            "detail": "No significant price, valuation, volume, or balance sheet signals detected."
        })

    severities = [s["severity"] for s in signals]
    if severities.count("Watch") >= 3:
        market_signal_level = "Elevated"
    elif "Watch" in severities:
        market_signal_level = "Watch"
    elif "Positive" in severities:
        market_signal_level = "Positive"
    else:
        market_signal_level = "Neutral"

    return {
        "ticker": ticker,
        "status": "ok",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "company_name":     company_name,
        "sector":           sector,
        "industry":         industry,
        "business_summary": business_summary,
        "website":          website,
        "employees":        employees,
        "country":          country,
        "current_price":      current_price,
        "previous_close":     previous_close,
        "open_price":         open_price,
        "day_high":           day_high,
        "day_low":            day_low,
        "week_52_high":       week_52_high,
        "week_52_low":        week_52_low,
        "week_52_position":   week_52_position,
        "price_change":       price_change,
        "price_change_pct":   price_change_pct,
        "volume":             volume,
        "avg_volume":         avg_volume,
        "volume_vs_avg":      volume_vs_avg,
        "market_cap":         market_cap,
        "market_cap_fmt":     _fmt_large(market_cap),
        "beta":               beta,
        "pe_ratio":       pe_ratio,
        "forward_pe":     forward_pe,
        "peg_ratio":      peg_ratio,
        "price_to_book":  price_to_book,
        "price_to_sales": price_to_sales,
        "ev_to_ebitda":   ev_to_ebitda,
        "ev_to_revenue":  ev_to_revenue,
        "eps_ttm":             eps_ttm,
        "eps_forward":         eps_forward,
        "revenue_ttm":         revenue_ttm,
        "revenue_ttm_fmt":     _fmt_large(revenue_ttm),
        "gross_margins":       gross_margins,
        "gross_margins_fmt":   _pct(gross_margins),
        "operating_margins":       operating_margins,
        "operating_margins_fmt":   _pct(operating_margins),
        "profit_margins":      profit_margins,
        "profit_margins_fmt":  _pct(profit_margins),
        "revenue_growth":      revenue_growth,
        "revenue_growth_fmt":  _pct(revenue_growth),
        "earnings_growth":     earnings_growth,
        "earnings_growth_fmt": _pct(earnings_growth),
        "earnings_date":       earnings_date,
        "total_cash":           total_cash,
        "total_cash_fmt":       _fmt_large(total_cash),
        "total_debt":           total_debt,
        "total_debt_fmt":       _fmt_large(total_debt),
        "debt_to_equity":       debt_to_equity,
        "current_ratio":        current_ratio,
        "quick_ratio":          quick_ratio,
        "free_cash_flow":       free_cash_flow,
        "free_cash_flow_fmt":   _fmt_large(free_cash_flow),
        "return_on_equity":     return_on_equity,
        "return_on_equity_fmt": _pct(return_on_equity),
        "return_on_assets":     return_on_assets,
        "return_on_assets_fmt": _pct(return_on_assets),
        "analyst_target":   analyst_target,
        "analyst_high":     analyst_high,
        "analyst_low":      analyst_low,
        "analyst_count":    analyst_count,
        "recommendation":   recommendation,
        "upside_to_target": upside_to_target,
        "dividend_rate":  dividend_rate,
        "dividend_yield": dividend_yield,
        "payout_ratio":   payout_ratio,
        "news":                news_items,
        "market_signal_level": market_signal_level,
        "market_signals":      signals,
    }
