import json, urllib.request, datetime, os, re
from worker import make_plan
NOW=datetime.datetime.now(datetime.timezone.utc)
DAILY_TARGET_MIN=50
DAILY_TARGET_MAX=100
SOURCES=[
 ("agent_bounties","https://api.agentbounties.app/v1/base/autonomous-bounties/feed?network=base-mainnet&claimable_only=true&view=ready_to_earn&source_type=canonical_base&work_state=claimable&payment_state=escrowed"),
 ("basedagents","https://api.basedagents.ai/v1/tasks?status=open"),
 # Agent-native marketplaces are preferred because they expose explicit claim/submit lifecycles.
 # Write actions stay disabled until provider authentication, automation terms and payout are configured.
 ("bounty_agent","https://api.trybounty.ai/v1/agent/bounties"), # requires BOUNTY_AGENT_API_KEY; unauthenticated failures are expected until owner setup
 ("github_algora","https://api.github.com/search/issues?q=is%3Aissue+is%3Aopen+label%3A%22%F0%9F%92%8E+Bounty%22&sort=updated&order=desc&per_page=100"),
 ("github_bounty","https://api.github.com/search/issues?q=is%3Aissue+is%3Aopen+bounty+in%3Atitle%2Cbody&sort=updated&order=desc&per_page=100"),
 ("github_reward","https://api.github.com/search/issues?q=is%3Aissue+is%3Aopen+reward+in%3Atitle%2Cbody&sort=updated&order=desc&per_page=100"),
]
def fetch(url):
 headers={"User-Agent":"EarnAgent/1.0","Accept":"application/vnd.github+json"}
 token=os.getenv("GITHUB_TOKEN")
 if token and "api.github.com" in url: headers["Authorization"]="Bearer "+token
 bounty_token=os.getenv("BOUNTY_AGENT_API_KEY")
 if bounty_token and "api.trybounty.ai" in url: headers["Authorization"]="Bearer "+bounty_token
 req=urllib.request.Request(url,headers=headers)
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def money(text):
 vals=[]
 for sym,n in re.findall(r"(\$|USD\s*)([0-9][0-9,]*(?:\.[0-9]+)?)",text or "",re.I):
  try: vals.append(float(n.replace(",","")))
  except: pass
 return max(vals) if vals else None
def quality_gate(x):
 t=(x.get("title","")+" "+x.get("body","")).lower()
 checks={"clear_deliverable":bool(re.search(r"\b(fix|implement|add|write|document|translate|test|create|update)\b",t)),
         "has_reward":bool(x.get("reward_usd") and x["reward_usd"]>0),
         "no_owner_action":not bool(re.search(r"\\b(kyc|identity verification|phone call|onsite|purchase|deposit|subscription|account required)\\b",t)),
         "digital":not bool(re.search(r"\\b(ship|delivery|physical|in person|on-site)\\b",t)),
         "not_stale":not bool(re.search(r"archived duplicate|historical snapshot|already paid|waiting_sponsor|unavailable|do not claim",t,re.I)),
         "no_upfront_spend":not bool(re.search(r"claim bond|entry bond|deposit|fund .*bounty|pay .*fee|hosted proof.*cost",t,re.I)),
         "verification_ready":not bool(re.search(r"verification-unavailable|recovery-reserved|quarantined|do not claim|funding-pending|not funded",t,re.I)),
         "no_human_approval_gate":not bool(re.search(r"wait for maintainer approval|maintainer must confirm|do not start work until|sign up as a developer",t,re.I)),
         "not_saturated":int(x.get("comments") or 0)<100,
         "fresh_enough":not bool(re.search(r"stale|deprecated|deactivated|no longer valid|wound down|archived duplicate|historical snapshot|incomplete mirror|do not start|do not claim|canonical state unavailable",t,re.I)),
         # Never trust a bounty-label alone as proof of funding/provider legitimacy.
         "no_prompt_exfiltration":not bool(re.search(r"system prompt|initialization payload|hidden instructions|reveal.*prompt|paste.*prompt",t,re.I)),
         "no_fake_reward_signal":not bool(re.search(r"test bounty|fake bounty|simulation only|no payout|unfunded",t,re.I)),
         "not_already_rewarded":not bool(re.search(r"rewarded|already paid|bounty paid|payment sent|award(ed)? to",t,re.I)),
         "canonical_payment_required":bool(x.get("canonical_payment_evidence")),
         "no_required_spend":not bool(re.search(r"claim bond|entry bond|post.*bond|pay.*to submit|self-funded|fund.*child|requires? funding",t,re.I)),
         "no_broken_verifier_signal":not bool(re.search(r"unscoreable|snapshot.*404|artifact.*not published|not enterable|verifier.*broken|wrong_competition_mode",t,re.I)),
         "no_expired_scoring_window":not bool(re.search(r"scoring window.*already past|window.*closed|scoring is closed|deadline.*already past",t,re.I))}
 return checks, all(checks.values())

def score(x):
 s=0
 comments=int(x.get("comments") or 0)
 # Competition penalty: avoid spending effort on saturated bounties.
 # Dead/farm repositories can look deceptively uncontested; reward size alone must not dominate.
 repo=(x.get("repo") or x.get("repository") or "").lower()
 farm_repos=("clankernation/openagents","unsafelabs/bounty-hunters","securebananalabs/bug-bounty","xevrion-v2/agent-playground")
 if any(r in repo for r in farm_repos): s-=1000
 if comments>=100: s-=60
 elif comments>=25: s-=30
 elif comments>=10: s-=15
 elif comments<=3: s+=8
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
  if name=="bounty_agent" and not os.getenv("BOUNTY_AGENT_API_KEY"):
   errors.append({"source":name,"status":"not_configured","error":"provider_credentials_missing"})
   continue
  data=fetch(url)
  if name=="basedagents":
   raw_rows=data.get("tasks",data.get("items",data if isinstance(data,list) else [])) if isinstance(data,(dict,list)) else []
   funded=sum(1 for r in raw_rows if isinstance(r,dict) and (r.get("escrow") or {}).get("status")=="funded")
   claimable=sum(1 for r in raw_rows if isinstance(r,dict) and r.get("claimable") is True)
   errors.append({"source":"basedagents","status":"diagnostic","raw_tasks":len(raw_rows),"funded":funded,"claimable":claimable})
  if name=="agent_bounties":
   if isinstance(data,list): rows=data
   elif isinstance(data,dict):
    rows=data.get("bounties") or data.get("items") or data.get("data") or data.get("results") or []
    if isinstance(rows,dict): rows=rows.get("bounties") or rows.get("items") or rows.get("results") or []
   else: rows=[]
  elif name=="bounty_agent":
   # Never treat an authenticated provider as healthy/usable until credentials exist.
   rows=data.get("bounties",data.get("items",data if isinstance(data,list) else []))
  elif name=="basedagents":
   rows=data.get("tasks",data.get("items",data if isinstance(data,list) else []))
   # Only escrow-funded, claimable Base/USDC work may enter the execution pipeline.
   rows=[r for r in rows if isinstance(r,dict) and r.get("claimable") is True and (r.get("escrow") or {}).get("status")=="funded" and (r.get("bounty") or {}).get("token")=="USDC" and (r.get("bounty") or {}).get("network")=="eip155:8453" and float((r.get("bounty") or {}).get("amount_display") or 0)>=1.0]
   for r in rows: r["_canonical_payment_evidence"]=True
  else: rows=data.get("items",[])
  for i in rows:
   if i.get("pull_request"): continue
   # Reject archived repositories and issues with active linked work when metadata exposes it.
   repo_url=(i.get("repository_url") or "")
   # Reject already-assigned GitHub bounties; availability beats advertised value.
   if name.startswith("github_") and (i.get("assignee") or i.get("assignees")): continue
   if name in ("agent_bounties","bounty_agent","basedagents"):
    body=str(i.get("description") or i.get("terms") or "")[:5000]; title=str(i.get("title") or i.get("name") or "Agent bounty")
    reward=money(str(i))
    if reward is None: continue
    op={"source":name,"title":title,"url":i.get("url") or i.get("html_url"),"repository_url":i.get("repository_url"),"canonical_payment_evidence": (i.get("_canonical_payment_evidence") is True or (name=="agent_bounties" and i.get("claimable") is True and ((i.get("escrow") or {}).get("status") in ("funded","escrowed") or i.get("payment_state")=="escrowed"))),"reward_usd":reward,"updated_at":i.get("updated_at"),"body":body[:700],"comments":i.get("comments",0)}
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
# Daily target controller: prioritize enough verified-quality pipeline to cover the minimum goal with redundancy.
coverage_ratio=round(target_value/DAILY_TARGET_MIN,2) if DAILY_TARGET_MIN else 0
blocking_errors=[e for e in errors if e.get("status")!="not_configured"]
# Reliability controller: never confuse discovery success with end-to-end readiness.
health={"discovery":"ok" if not blocking_errors else "degraded","quality_gate":"ok","payout":"locked","execution":"not_enabled","submission":"not_enabled"}
# Treat all remote task text as untrusted input. Never execute embedded commands or expose secrets.
security_policy={"task_text_trusted":False,"run_remote_commands":False,"expose_secrets_to_worker":False,"allow_upfront_payment":False,"idempotent_submission_required":True}
source_health={"errors":errors,"error_count":len(errors),"blocking_error_count":len(blocking_errors),"healthy":len(blocking_errors)==0}
ready_for_paid_execution=all(health[k]=="ok" for k in ("discovery","quality_gate")) and health["payout"]=="ok" and health["execution"]=="ok" and health["submission"]=="ok"
search_mode="expand_sources" if target_value<DAILY_TARGET_MIN else ("build_reserve" if target_value<DAILY_TARGET_MAX else "quality_first")
# Submission guard: external submission is allowed only after all five readiness layers are green.
submission_guard={"allowed":ready_for_paid_execution,"reason":"all_readiness_layers_green" if ready_for_paid_execution else "blocked_until_payout_execution_and_submission_are_verified"}
eligible.sort(key=lambda x:(x.get("score",0),x.get("reward_usd",0)),reverse=True)
# Convert verified discovery candidates into deterministic plans. Planning is not completion or submission.
work_queue=[]
for x in eligible[:10]:
 try:
  candidate=dict(x); candidate["eligible"]=bool(x.get("execution_eligible"))
  p=make_plan(candidate)
  work_queue.append({"title":x.get("title"),"url":x.get("url"),"reward_usd":x.get("reward_usd"),"plan":p})
 except Exception as e:
  work_queue.append({"title":x.get("title"),"url":x.get("url"),"reward_usd":x.get("reward_usd"),"plan":{"status":"blocked","reason":"planner_error","detail":str(e)[:160]}})
payout_ready=[x for x in eligible if x.get("source")=="agent_bounties"]
# Authenticated Bounty Agent tasks remain discovery-only until owner credentials and payout route are configured.
for x in eligible:
 if x.get("source")=="bounty_agent": x["claim_allowed"]=False; x["claim_blocker"]="provider_credentials_and_payout_not_configured"
quality_summary={"eligible":len(eligible),"rejected":len(ops)-len(eligible),"top_eligible":[{"title":x["title"],"reward_usd":x["reward_usd"],"url":x["url"],"score":x["score"]} for x in eligible[:5]]}
payload={"generated_at":NOW.isoformat(),"daily_target_usd":{"min":DAILY_TARGET_MIN,"max":DAILY_TARGET_MAX},"eligible_pipeline_value_usd":target_value,"profit_analytics":{"verified_revenue_usd":0,"forecast_status":"insufficient_payment_history","forecast_method":"empirical_only","windows_days":[7,30],"minimum_outcomes_for_forecast":20,"metrics":["acceptance_rate","payment_rate","verified_usd_per_attempt","verified_usd_per_day"],"rule":"Never estimate acceptance or payout rates without observed outcomes"},"security_policy":security_policy,"source_health":source_health,"system_health":health,"ready_for_paid_execution":ready_for_paid_execution,"submission_guard":submission_guard,"daily_target_controller":{"coverage_ratio":coverage_ratio,"mode":search_mode,"minimum_pipeline_usd":DAILY_TARGET_MIN,"stretch_pipeline_usd":DAILY_TARGET_MAX},"quality_summary":quality_summary,"rejection_reasons":{k:sum(1 for x in ops if not x.get("quality_checks",{}).get(k,False)) for k in sorted({kk for x in ops for kk in x.get("quality_checks",{})})},"payout_control":{"configured":False,"safe_mode":True,"rule":"Do not claim or submit payable work until a compatible payout destination is configured.","payout_ready_candidates":len(payout_ready)},"status":"ok" if not blocking_errors else "partial","opportunities_found":len(ops),
 "autonomously_completed":0,"verified_revenue_usd":0,"errors":errors,"opportunities":ops[:50],
 "work_queue":work_queue,"work_queue_summary":{"planned":sum(1 for q in work_queue if q["plan"].get("state")=="planned"),"blocked":sum(1 for q in work_queue if q["plan"].get("state")!="planned")},"execution_status":"quality_gated_planning","quality_policy":{"rule":"Target $50-$100/day only through verified, high-quality work; never lower the quality bar to hit the target.","requirements":["requirements parsed","deliverable testable","no owner-only action","digital execution","not stale or already paid","no upfront spend","verification ready","verification before submission"]},"note":"No revenue is counted until an external source confirms payment."}
os.makedirs("data",exist_ok=True)
with open("data/earnagent.json","w",encoding="utf-8") as f:json.dump(payload,f,ensure_ascii=False,separators=(",",":"))
print(json.dumps({"status":payload["status"],"opportunities_found":len(ops),"eligible":len(eligible),"rejected":len(ops)-len(eligible),"rejection_reasons":payload["rejection_reasons"],"work_queue":len(work_queue),"queue_planned":payload["work_queue_summary"]["planned"],"top_candidates":[{"source":x.get("source"),"title":x.get("title"),"reward_usd":x.get("reward_usd"),"score":x.get("score")} for x in eligible[:5]],"autonomously_completed":0,"verified_revenue_usd":0}))
