"""Office Fixer: repairs malformed AI-office decisions before execution.

The Fixer is deliberately narrower than the Executor: it may repair structure,
missing fields, contradictions and unsafe recommendations, but it cannot authorize
paid actions or external side effects.
"""
import json, os, urllib.request

REQUIRED = ("decision",)
BLOCKED = ("credential","private key","password","api key","sign in","login","impersonat","send an email","make a payment","purchase","deposit")

def validate(review):
    if not isinstance(review, dict):
        return False, ["review_not_object"]
    missing=[k for k in REQUIRED if not review.get(k)]
    if missing: return False, ["missing:"+k for k in missing]
    blob=json.dumps(review,ensure_ascii=False).lower()
    bad=[x for x in BLOCKED if x in blob]
    if bad: return False, ["unsafe:"+x for x in bad]
    if review.get("decision") not in ("execute","skip","revise","hold"):
        return False, ["invalid_decision"]
    return True, []

def repair(review, task, fmt):
    ok, errors=validate(review)
    if ok:
        review=dict(review)
        review["fixer"]="validated"
        return review
    key=os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    model=os.environ.get("EARNAGENT_FIXER_MODEL","gpt-6-luna")
    prompt={"review":review,"validation_errors":errors,"task":task,"format":fmt,
            "instruction":"Repair only the office decision JSON. Preserve useful findings. Remove unsafe or unverifiable actions. Never authorize credentials, account access, payments, purchases, spam, impersonation or illegal activity. Return JSON only."}
    body=json.dumps({"model":model,"input":[
        {"role":"system","content":"You are the Office Fixer. You repair another AI worker's malformed or unsafe office result. You are not allowed to invent payment evidence or authorize side effects."},
        {"role":"user","content":json.dumps(prompt,ensure_ascii=False)}],"max_output_tokens":2500}).encode()
    req=urllib.request.Request("https://api.openai.com/v1/responses",data=body,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            data=json.loads(r.read().decode())
        fixed=json.loads(data.get("output_text","").strip())
        ok2,errors2=validate(fixed)
        if not ok2: return None
        fixed["fixer"]="ai-repaired"
        fixed["fixer_model"]=model
        return fixed
    except Exception:
        return None
