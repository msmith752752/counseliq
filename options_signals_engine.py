"""
options_signals_engine.py
CounselIQ — Options Intelligence Module

Pulls options chain data from yfinance and surfaces unusual activity signals:
- Volume vs. open interest ratio (fresh positioning)
- Call/put skew
- Relative volume vs. average (approximated)
- IV rank context
- Top unusual contracts
- Signal level: Elevated / Watch / Neutral
"""

import yfinance as yf


def _safe(val, default=None):
    try:
        if val is None:
            return default
        v = float(val)
        import math
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default


def _fmt(val, decimals=2, default="N/A"):
    v = _safe(val)
    if v is None:
        return default
    return f"{v:,.{decimals}f}"


def _pct(val, default="N/A"):
    v = _safe(val)
    if v is None:
        return default
    return f"{v:.1f}%"


def build_options_signals(ticker: str) -> dict:
    try:
        tk = yf.Ticker(ticker.upper())

        # Get current price for context
        info = tk.fast_info
        current_price = _safe(getattr(info, "last_price", None))

        # Get all available expiration dates
        expirations = tk.options
        if not expirations:
            return _empty(ticker, "No options data available for this ticker.")

        # Pull chains for the nearest 3 expirations (most active)
        all_calls = []
        all_puts = []

        for exp in expirations[:3]:
            try:
                chain = tk.option_chain(exp)
                calls = chain.calls.copy()
                puts = chain.puts.copy()
                calls["expiration"] = exp
                puts["expiration"] = exp
                all_calls.append(calls)
                all_puts.append(puts)
            except Exception:
                continue

        if not all_calls:
            return _empty(ticker, "Could not load options chain.")

        import pandas as pd
        calls_df = pd.concat(all_calls, ignore_index=True)
        puts_df = pd.concat(all_puts, ignore_index=True)

        # ── Aggregate volume stats ──────────────────────────────────────────
        total_call_vol = int(calls_df["volume"].fillna(0).sum())
        total_put_vol = int(puts_df["volume"].fillna(0).sum())
        total_vol = total_call_vol + total_put_vol

        call_pct = round(total_call_vol / total_vol * 100, 1) if total_vol > 0 else 0
        put_pct = round(total_put_vol / total_vol * 100, 1) if total_vol > 0 else 0
        pc_ratio = round(total_put_vol / total_call_vol, 2) if total_call_vol > 0 else None

        # ── Volume / Open Interest ratio (fresh positioning signal) ──────────
        calls_df["vol_oi_ratio"] = calls_df.apply(
            lambda r: _safe(r["volume"]) / _safe(r["openInterest"])
            if _safe(r["openInterest"], 0) > 0 and _safe(r["volume"], 0) > 0
            else None,
            axis=1,
        )
        puts_df["vol_oi_ratio"] = puts_df.apply(
            lambda r: _safe(r["volume"]) / _safe(r["openInterest"])
            if _safe(r["openInterest"], 0) > 0 and _safe(r["volume"], 0) > 0
            else None,
            axis=1,
        )

        # ── Top unusual CALL contracts ────────────────────────────────────────
        # Filter: volume > 100, vol/OI > 0.5 (meaningful fresh activity)
        unusual_calls = calls_df[
            (calls_df["volume"].fillna(0) > 100) &
            (calls_df["vol_oi_ratio"].fillna(0) > 0.5)
        ].copy()

        unusual_calls = unusual_calls.sort_values("vol_oi_ratio", ascending=False).head(5)

        top_contracts = []
        for _, row in unusual_calls.iterrows():
            strike = _safe(row.get("strike"))
            vol = _safe(row.get("volume"))
            oi = _safe(row.get("openInterest"))
            iv = _safe(row.get("impliedVolatility"))
            voi = _safe(row.get("vol_oi_ratio"))
            exp = row.get("expiration", "")
            last = _safe(row.get("lastPrice"))

            # OTM/ITM context
            moneyness = "N/A"
            if current_price and strike:
                diff_pct = (strike - current_price) / current_price * 100
                if diff_pct > 5:
                    moneyness = f"OTM +{diff_pct:.1f}%"
                elif diff_pct < -5:
                    moneyness = f"ITM {diff_pct:.1f}%"
                else:
                    moneyness = f"ATM ({diff_pct:+.1f}%)"

            top_contracts.append({
                "type": "CALL",
                "strike": _fmt(strike),
                "expiration": exp,
                "moneyness": moneyness,
                "volume": int(vol) if vol else 0,
                "open_interest": int(oi) if oi else 0,
                "vol_oi_ratio": _fmt(voi),
                "implied_volatility": _pct(iv * 100 if iv else None),
                "last_price": _fmt(last),
            })

        # ── IV summary ────────────────────────────────────────────────────────
        avg_call_iv = calls_df["impliedVolatility"].dropna().mean()
        avg_put_iv = puts_df["impliedVolatility"].dropna().mean()
        iv_skew = "Put premium (bearish skew)" if avg_put_iv > avg_call_iv * 1.1 \
            else "Call premium (bullish skew)" if avg_call_iv > avg_put_iv * 1.1 \
            else "Neutral"

        # ── Signal detection ──────────────────────────────────────────────────
        signals = []

        # Call dominance
        if call_pct >= 70:
            signals.append({
                "signal": "Heavy Call Dominance",
                "detail": f"{call_pct}% of volume is calls — strong bullish positioning bias.",
                "severity": "watch"
            })
        elif call_pct >= 60:
            signals.append({
                "signal": "Call Volume Skew",
                "detail": f"{call_pct}% of volume is calls — mild bullish bias.",
                "severity": "positive"
            })

        # Put dominance
        if put_pct >= 65:
            signals.append({
                "signal": "Put Volume Elevated",
                "detail": f"{put_pct}% of volume is puts — elevated hedging or bearish positioning.",
                "severity": "watch"
            })

        # High vol/OI unusual contracts
        if len(top_contracts) >= 3:
            signals.append({
                "signal": "Multiple Unusual Call Contracts",
                "detail": f"{len(top_contracts)} call contracts with volume exceeding open interest — new positioning entering.",
                "severity": "watch"
            })
        elif len(top_contracts) >= 1:
            signals.append({
                "signal": "Unusual Call Activity",
                "detail": f"{len(top_contracts)} call contract(s) with Vol/OI > 0.5 — potential fresh bullish positioning.",
                "severity": "positive"
            })

        # IV skew signal
        if "bullish" in iv_skew.lower():
            signals.append({
                "signal": "Bullish IV Skew",
                "detail": "Calls carrying higher implied volatility than puts — options market pricing upside risk.",
                "severity": "positive"
            })
        elif "bearish" in iv_skew.lower():
            signals.append({
                "signal": "Bearish IV Skew",
                "detail": "Puts carrying higher implied volatility than calls — hedging activity elevated.",
                "severity": "watch"
            })

        # Low P/C ratio (very bullish options sentiment)
        if pc_ratio is not None and pc_ratio < 0.4:
            signals.append({
                "signal": "Low Put/Call Ratio",
                "detail": f"P/C ratio of {pc_ratio} — unusually low, indicating strong call-side conviction.",
                "severity": "watch"
            })

        # ── Signal level ──────────────────────────────────────────────────────
        watch_count = sum(1 for s in signals if s["severity"] == "watch")
        positive_count = sum(1 for s in signals if s["severity"] == "positive")

        if watch_count >= 2:
            signal_level = "Elevated"
        elif watch_count == 1:
            signal_level = "Watch"
        elif positive_count >= 1:
            signal_level = "Positive"
        else:
            signal_level = "Neutral"

        return {
            "ticker": ticker.upper(),
            "options_signal_level": signal_level,
            "options_signals": signals,
            "expirations_analyzed": list(expirations[:3]),
            "summary": {
                "total_call_volume": total_call_vol,
                "total_put_volume": total_put_vol,
                "call_pct": call_pct,
                "put_pct": put_pct,
                "put_call_ratio": pc_ratio,
                "avg_call_iv": _pct(avg_call_iv * 100 if _safe(avg_call_iv) else None),
                "avg_put_iv": _pct(avg_put_iv * 100 if _safe(avg_put_iv) else None),
                "iv_skew": iv_skew,
                "unusual_contracts_found": len(top_contracts),
            },
            "top_unusual_calls": top_contracts,
            "error": None,
        }

    except Exception as e:
        return _empty(ticker, str(e))


def _empty(ticker, error_msg):
    return {
        "ticker": ticker.upper(),
        "options_signal_level": "Neutral",
        "options_signals": [],
        "expirations_analyzed": [],
        "summary": {
            "total_call_volume": 0,
            "total_put_volume": 0,
            "call_pct": 0,
            "put_pct": 0,
            "put_call_ratio": None,
            "avg_call_iv": "N/A",
            "avg_put_iv": "N/A",
            "iv_skew": "N/A",
            "unusual_contracts_found": 0,
        },
        "top_unusual_calls": [],
        "error": error_msg,
    }
