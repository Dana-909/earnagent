import json, urllib.request, datetime, os, re
NOW=datetime.datetime.now(datetime.timezone.utc)
DAILY_TARGET_MIN=50
DAILY_TARGET_MAX=100
SOURCES=[
 ("agent_bounties","https://api.agentbounties.app/v1/base/autonomous-bounties/feed?network=base-mainnet&claimable_only=true"),
 ("github_bounty","https://api.github.com/search/issues?q=is%3Aissue+is%3Aopen+bounty+in%3Atitle%2Cbody&sort=updated&order=desc&per_page=100"),
 ("github_reward","https://api.github.com/search/issues?q=is%3Aissue+is%3Aopen+reward+in%3Atitle%2Cbody&sort=updated&order=desc&per_page=100"),
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
def quality_gate(x):
 t=(x.get("title","")+" "+x.get("body","")).lower()
 checks={"clear_deliverable":bool(re.search(r"\\b(fix|implement|add|write|document|translate|test|create|update)\\b",t)),
         "has_reward":bool(x.get("reward_usd") and x["reward_usd"]>0),
         "no_owner_action":not bool(re.search(r"\\b(kyc|identity verification|phone call|onsite|purchase|deposit|subscription|account required)\\b",t)),
         "digital":not bool(re.search(r"\\b(ship|delivery|physical|in person|on-site)\\b",t)),
         "not_stale":not bool(re.search(r"archived duplicate|historical snapshot|already paid|waiting_sponsor|unavailable|do not claim",t,re.I)),
         "no_upfront_spend":not bool(re.search(r"claim bond|entry bond|deposit|fund .*bounty|pay .*fee|hosted proof.*cost",t,re.I))}
 return checks, all(checks.values())

def score(x):
 s=0
 if x.get("reward_usd"): s+=min(60,x["reward_usd"]/10)
 t=(x.get("title","")+" "+x.get("body","")).lower()
 for k in ("documentation","docs","readme","translation","python","javascript","data","test"): 
  if k in t:s+=4
 for k in ("design","onsite","phone","physical","kyc","deposit","pay to","purchase","archived duplicate","waiting_sponsor","unavailable","verification-unavailable","signup","register","claim bond","entry bond"):
  if k in t:s-=12
 return round(s,1)
ops=[]; errors=[]
for name,url in SOURCES:
 try:
  data=fetch(url)
  if name=="agent_bounties":
   rows=data.get("bounties",data.get("items",data if isinstance(data,list) else []))
  else: rows=data.get("items",[])
  for i in rows:
   if i.get("pull_request"): continue
   if name=="agent_bounties":
    body=str(i.get("description") or i.get("terms") or "")[:5000]; title=str(i.get("title") or i.get("name") or "Agent bounty")
    reward=money(str(i))
    if reward is None: continue
    op={"source":name,"title":title,"url":i.get("url") or i.get("html_url"),"repository_url":i.get("repository_url"),"reward_usd":reward,"updated_at":i.get("updated_at"),"body":body[:700]}
    op["score"]=score(op); op["quality_checks"],op["execution_eligible"]=quality_gate(op); ops.append(op); continue
   body=(i.get("body") or "")[:5000]; title=i.get("title") or ""
   reward=money(title+" "+body)
   # Do not pretend vague mentions are payable work: require explicit bounty/reward and a numeric USD amount.
   if reward is None or not re.search(r"\b(bounty|reward)\b",title+" "+body,re.I): continue
   op={"source":name,"title":title,"url":i.get("html_url"),"repository_url":i.get("repository_url"),
       "reward_usd":reward,"updated_at":i.get("updated_at"),"body":body[:700]}
   op["score"]=score(op); op["quality_checks"],op["execution_eligible"]=quality_gate(op); ops.append(op)
 except Exception as e: errors.append({"source":name,"error":str(e)})
dedup={x["url"]:x for x in ops if x.get("url")}
ops=list(dedup.values())
ops.sort(key=lambda x:(x["execution_eligible"],x["score"],x["reward_usd"]),reverse=True)
# This agent deliberately does not claim/submission-spam third-party tasks without repository-level validation.
# It autonomously scouts and ranks only; execution is enabled only for tasks whose requirements can be verified programmatically.
eligible=[x for x in ops if x.get("execution_eligible")]
target_value=sum(x.get("reward_usd",0) for x in eligible[:5])
payload={"generated_at":NOW.isoformat(),"daily_target_usd":{"min":DAILY_TARGET_MIN,"max":DAILY_TARGET_MAX},"eligible_pipeline_value_usd":target_value,"status":"ok" if not errors else "partial","opportunities_found":len(ops),
 "autonomously_completed":0,"verified_revenue_usd":0,"errors":errors,"opportunities":ops[:50],
 "execution_status":"quality_gated_scouting","quality_policy":{"rule":"Target $50-$100/day only through verified, high-quality work; never lower the quality bar to hit the target.","requirements":["requirements parsed","deliverable testable","no owner-only action","digital execution","not stale or already paid","no upfront spend","verification before submission"]},"note":"No revenue is counted until an external source confirms payment."}
os.makedirs("data",exist_ok=True)
with open("data/earnagent.json","w",encoding="utf-8") as f:json.dump(payload,f,ensure_ascii=False,separators=(",",":"))
print(json.dumps({k:payload[k] for k in ("status","opportunities_found","autonomously_completed","verified_revenue_usd")}))
