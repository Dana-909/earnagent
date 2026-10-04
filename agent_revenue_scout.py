#!/usr/bin/env python3
"""Agent-native revenue scout: public Circle x402 catalog + Agent Souk evidence."""
import json, os, time, urllib.request
from pathlib import Path

OUT=Path("data/agent_revenue_market.json")
CIRCLE="https://api.circle.com/v2/x402/discovery/resources"
UA="EarnAgent-revenue-scout/1.0"

def get(url):
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":UA})
        with urllib.request.urlopen(req,timeout=20) as r:
            return {"ok":True,"status":r.status,"data":json.loads(r.read().decode())}
    except Exception as e:
        return {"ok":False,"error":str(e)[:240]}

def rows(x):
    if isinstance(x,list): return x
    if isinstance(x,dict):
        for k in ("resources","items","data","results"):
            if isinstance(x.get(k),list): return x[k]
    return []

def price(x):
    for k in ("priceUsd","price_usd","usdPrice","amountUsd"):
        try:
            if x.get(k) is not None: return float(x[k])
        except: pass
    a=x.get("accepts") if isinstance(x,dict) else None
    if isinstance(a,dict):
        try:
            n=float(a.get("amount"))
            return n/1_000_000 if n>=1000 else n
        except: pass
    return None

def clean(x):
    if not isinstance(x,dict): return x
    bad=("authorization","token","secret","private","api_key","apiKey")
    return {k:v for k,v in x.items() if not any(b in str(k).lower() for b in bad)}

def main():
    r=get(CIRCLE)
    services=rows(r.get("data")) if r.get("ok") else []
    paid=[clean(x) for x in services if price(x) is not None and price(x)>0]
    paid.sort(key=lambda x: price(x) or 999999)
    cats={}
    for x in paid:
        c=str(x.get("category") or (x.get("metadata") or {}).get("category") or "unknown")
        cats[c]=cats.get(c,0)+1
    out={
      "generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "read_only":True,
      "source":CIRCLE,
      "revenue_verified_usd":0,
      "rule":"Catalog presence and endpoint prices are market evidence, not EarnAgent revenue.",
      "api":{"ok":r.get("ok"),"status":r.get("status"),"error":r.get("error")},
      "catalog_count":len(services),
      "priced_count":len(paid),
      "categories":cats,
      "sample_paid_endpoints":paid[:150],
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"catalog_count":len(services),"priced_count":len(paid),"categories":cats},ensure_ascii=False))
if __name__=="__main__": main()
