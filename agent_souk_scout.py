#!/usr/bin/env python3
"""Public Agent Souk market scout.

Read-only discovery. Never registers an agent, binds a wallet, spends funds,
or publishes credentials. The output distinguishes priced/live evidence from
search-interest signals so revenue is never fabricated.
"""
import json
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = os.environ.get("AGENTSOUK_API", "https://api.agentsouk.dev").rstrip("/")
OUT = Path("data/agent_souk_market.json")
TIMEOUT = int(os.environ.get("AGENTSOUK_TIMEOUT", "20"))

def get(path):
    req = urllib.request.Request(
        BASE + path,
        headers={"Accept": "application/json", "User-Agent": "EarnAgent-market-scout/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            return {"ok": True, "status": r.status, "data": json.loads(raw.decode("utf-8"))}
    except Exception as e:
        return {"ok": False, "error": str(e)[:240]}

def rows(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("items", "bounties", "listings", "opportunities", "results", "data"):
            if isinstance(data.get(k), list):
                return data[k]
    return []

def amount_usdc(x):
    for k in ("budget", "reward", "price", "amount", "max_budget", "maxBudget"):
        v = x.get(k) if isinstance(x, dict) else None
        if isinstance(v, dict):
            v = v.get("amount") or v.get("value") or v.get("usdc")
        if v is None:
            continue
        try:
            n = float(v)
            # Agent Souk commonly represents USDC prices in minor units.
            return n / 1_000_000 if n >= 1000 else n
        except Exception:
            pass
    return None

def clean(x):
    if not isinstance(x, dict):
        return x
    # Public market evidence only; never persist headers, tokens, signatures, or keys.
    blocked = ("authorization", "token", "secret", "private_key", "privateKey", "api_key", "apiKey")
    return {k: v for k, v in x.items() if str(k) not in blocked}

def main():
    endpoints = {
        "demand": "/v1/demand",
        "listings": "/v1/listings",
        "opportunities": "/v1/opportunities",
    }
    fetched = {name: get(path) for name, path in endpoints.items()}
    demand = rows(fetched["demand"].get("data")) if fetched["demand"].get("ok") else []
    listings = rows(fetched["listings"].get("data")) if fetched["listings"].get("ok") else []
    opportunities = rows(fetched["opportunities"].get("data")) if fetched["opportunities"].get("ok") else []

    priced_demand = []
    for x in demand:
        x = clean(x)
        price = amount_usdc(x)
        if price is not None and price > 0:
            x["_budget_usdc"] = price
            priced_demand.append(x)

    priced_listings = []
    for x in listings:
        x = clean(x)
        price = amount_usdc(x)
        if price is not None and price > 0:
            x["_price_usdc"] = price
            priced_listings.append(x)

    # Rank only by evidence that includes a monetary value. Search terms without
    # a budget remain visible but can never become a "revenue opportunity".
    priced_demand.sort(key=lambda x: x.get("_budget_usdc", 0), reverse=True)
    priced_listings.sort(key=lambda x: x.get("_price_usdc", 0), reverse=True)

    out = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": BASE,
        "read_only": True,
        "revenue_verified_usd": 0,
        "rule": "Only settled on-chain payments may be counted as revenue. Search traffic, listings, and bounties are opportunities, not earnings.",
        "api_status": {k: {"ok": v.get("ok"), "status": v.get("status"), "error": v.get("error")} for k,v in fetched.items()},
        "evidence": {
            "priced_demand": priced_demand[:100],
            "priced_listings": priced_listings[:100],
            "opportunities": [clean(x) for x in opportunities[:100]],
            "search_demand_unpriced": [clean(x) for x in demand[:100] if amount_usdc(x) in (None, 0)],
        },
        "counts": {
            "priced_demand": len(priced_demand),
            "priced_listings": len(priced_listings),
            "opportunities": len(opportunities),
            "demand_total": len(demand),
            "listings_total": len(listings),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out["counts"], ensure_ascii=False))

if __name__ == "__main__":
    main()
