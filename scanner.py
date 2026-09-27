import json, urllib.request, datetime, os
URL="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1000"
req=urllib.request.Request(URL,headers={"User-Agent":"ParadoxEngine/0.3"})
with urllib.request.urlopen(req,timeout=30) as r: markets=json.load(r)
rows=[]
for m in markets:
    try:
        prices=json.loads(m.get("outcomePrices") or "[]")
        yes=float(prices[0]) if prices else None
    except: yes=None
    rows.append({"id":m.get("id"),"question":m.get("question"),"slug":m.get("slug"),"yes":yes,
      "liquidity":m.get("liquidity"),"volume":m.get("volume"),"endDate":m.get("endDate"),
      "description":m.get("description") or m.get("rules") or "", "bestBid":m.get("bestBid"), "bestAsk":m.get("bestAsk"), "spread":m.get("spread"), "clobTokenIds":m.get("clobTokenIds")})
os.makedirs("data",exist_ok=True)
with open("data/markets.json","w",encoding="utf-8") as f:
 json.dump({"generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"count":len(rows),"markets":rows},f,ensure_ascii=False,separators=(",",":"))
print("markets",len(rows))
