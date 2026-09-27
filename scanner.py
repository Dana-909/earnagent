import json, urllib.request, datetime, os, re
URL="https://gamma-api.polymarket.com/markets?active=true&closed=false&limit=1000"
NOW=datetime.datetime.now(datetime.timezone.utc)
MONTHS={m:i+1 for i,m in enumerate("january february march april may june july august september october november december".split())}
DATE_RE=re.compile(r"\\b("+"|".join(MONTHS)+r")\\s+(\\d{1,2})(?:st|nd|rd|th)?(?:,?\\s+(20\\d{2}))?",re.I)

def num(x):
    try:return float(x)
    except:return None
def yes_price(m):
    try:
        p=json.loads(m.get("outcomePrices") or "[]"); return float(p[0]) if p else None
    except:return None
def date_of(s):
    x=DATE_RE.search(s or "")
    if not x:return None
    try:return datetime.datetime(int(x.group(3) or NOW.year),MONTHS[x.group(1).lower()],int(x.group(2)),tzinfo=datetime.timezone.utc)
    except:return None
def signature(s):
    s=DATE_RE.sub(" DATE ",(s or "").lower())
    s=re.sub(r"[^a-z0-9]+"," ",s)
    s=re.sub(r"\\b(by|before|on|date|will|the|a|an)\\b"," ",s)
    return re.sub(r"\\s+"," ",s).strip()
def rule_similarity(a,b):
    def words(x):return {z for z in re.split(r"\\W+",x.lower()) if len(z)>4}
    A,B=words(a or ""),words(b or "")
    if not A or not B:return None
    return len(A&B)/max(1,min(len(A),len(B)))

req=urllib.request.Request(URL,headers={"User-Agent":"ParadoxEngine/1.0"})
status="ok"; error=None
try:
    with urllib.request.urlopen(req,timeout=30) as r: raw=json.load(r)
except Exception as e:
    raw=[]; status="error"; error=str(e)

markets=[]
for m in raw:
    markets.append({"id":m.get("id"),"question":m.get("question") or "","slug":m.get("slug"),"yes":yes_price(m),
      "liquidity":num(m.get("liquidity")),"volume":num(m.get("volume")),"endDate":m.get("endDate"),
      "description":m.get("description") or m.get("rules") or "","bestBid":num(m.get("bestBid")),
      "bestAsk":num(m.get("bestAsk")),"spread":num(m.get("spread")),"clobTokenIds":m.get("clobTokenIds")})

groups={}
for m in markets:
    d=date_of(m["question"]); p=m["yes"]; sig=signature(m["question"])
    if d and p is not None and len(sig)>=8: groups.setdefault(sig,[]).append((d,m))

pairs=0; flags=[]
for g in groups.values():
    g.sort(key=lambda z:z[0])
    for i in range(len(g)):
      for j in range(i+1,len(g)):
        pairs+=1; a,b=g[i][1],g[j][1]; rawgap=a["yes"]-b["yes"]
        if rawgap<=.005: continue
        sim=rule_similarity(a["description"],b["description"])
        liq=min(a["liquidity"] or 0,b["liquidity"] or 0)
        executable=(a["bestBid"]-b["bestAsk"]) if a["bestBid"] is not None and b["bestAsk"] is not None else None
        qualified=bool(executable is not None and executable>0 and liq>=1000 and sim is not None and sim>.70)
        flags.append({"earlier":a,"later":b,"raw_gap":rawgap,"executable_gap":executable,"min_liquidity":liq,
          "rule_similarity":sim,"qualified_paper":qualified})
flags.sort(key=lambda x:(x["qualified_paper"],x["executable_gap"] if x["executable_gap"] is not None else -999,x["raw_gap"]),reverse=True)
os.makedirs("data",exist_ok=True)
payload={"generated_at":NOW.isoformat(),"status":status,"error":error,"market_count":len(markets),"candidate_pairs":pairs,
 "logical_flags":len(flags),"qualified_paper_candidates":sum(1 for x in flags if x["qualified_paper"]),"candidates":flags[:100]}
with open("data/results.json","w",encoding="utf-8") as f: json.dump(payload,f,ensure_ascii=False,separators=(",",":"))
with open("data/markets.json","w",encoding="utf-8") as f: json.dump({"generated_at":NOW.isoformat(),"count":len(markets),"markets":markets},f,ensure_ascii=False,separators=(",",":"))
print(json.dumps({k:payload[k] for k in ("status","market_count","candidate_pairs","logical_flags","qualified_paper_candidates")}))
if status!="ok": raise SystemExit(1)
