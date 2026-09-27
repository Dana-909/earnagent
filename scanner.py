import json, urllib.request, datetime, os, re
NOW=datetime.datetime.now(datetime.timezone.utc)
SOURCES=[
 ("github_bounties","https://api.github.com/search/issues?q=is%3Aopen+%28bounty+OR+reward%29+in%3Atitle%2Cbody&sort=updated&order=desc&per_page=100"),
]
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"EarnAgent/1.0","Accept":"application/vnd.github+json"})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def money(text):
 vals=[]
 for sym,n in re.findall(r"(\$|USD\s*)([0-9][0-9,]*(?:\.[0-9]+)?)",text or "",re.I):
  try: vals.append(float(n.replace(",","")))
  except: pass
 return max(vals) if vals else None
def score(x):
 s=0
 if x.get("reward_usd"): s+=min(60,x["reward_usd"]/10)
 t=(x.get("title","")+" "+x.get("body","")).lower()
 for k in ("documentation","docs","readme","translation","python","javascript","data","test"): 
  if k in t:s+=4
 for k in ("design","onsite","phone","physical","kyc","deposit","pay to","purchase"):
  if k in t:s-=12
 return round(s,1)
ops=[]; errors=[]
for name,url in SOURCES:
 try:
  data=fetch(url)
  for i in data.get("items",[]):
   if i.get("pull_request"): continue
   body=(i.get("body") or "")[:5000]; title=i.get("title") or ""
   reward=money(title+" "+body)
   # Do not pretend vague mentions are payable work: require explicit bounty/reward and a numeric USD amount.
   if reward is None or not re.search(r"\b(bounty|reward)\b",title+" "+body,re.I): continue
   op={"source":name,"title":title,"url":i.get("html_url"),"repository_url":i.get("repository_url"),
       "reward_usd":reward,"updated_at":i.get("updated_at"),"body":body[:700]}
   op["score"]=score(op); ops.append(op)
 except Exception as e: errors.append({"source":name,"error":str(e)})
ops.sort(key=lambda x:(x["score"],x["reward_usd"]),reverse=True)
# This agent deliberately does not claim/submission-spam third-party tasks without repository-level validation.
# It autonomously scouts and ranks only; execution is enabled only for tasks whose requirements can be verified programmatically.
payload={"generated_at":NOW.isoformat(),"status":"ok" if not errors else "partial","opportunities_found":len(ops),
 "autonomously_completed":0,"verified_revenue_usd":0,"errors":errors,"opportunities":ops[:50],
 "execution_status":"scouting","note":"No revenue is counted until an external source confirms payment."}
os.makedirs("data",exist_ok=True)
with open("data/earnagent.json","w",encoding="utf-8") as f:json.dump(payload,f,ensure_ascii=False,separators=(",",":"))
print(json.dumps({k:payload[k] for k in ("status","opportunities_found","autonomously_completed","verified_revenue_usd")}))
