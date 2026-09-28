import json, os, re, subprocess, sys, xml.etree.ElementTree as ET
TASK_ID="0x1d63afca637422566509350819d66be837192535849240bed49104258cd45a49"
AGENT="0x948B78F80ba73E846B27171f31E3609b0e399701".lower()
FILE="deliverables/natures_strange_eyes.svg"
def cli(*args):
    p=subprocess.run(["taskmarket",*args],capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr or p.stdout)
    return json.loads(p.stdout)
raw=open(FILE,"rb").read(); text=raw.decode()
assert len(raw)<=500000; ET.fromstring(text)
assert text.count('id="entry-')==5
assert all(x in text for x in ["Felis catus","Capra hircus","Equus caballus","Panthera tigris","Sepia bandensis"])
assert "SCHEMATIC CAVEAT" in text and "<title" in text and "<desc" in text
assert "<script" not in text.lower() and "<foreignObject" not in text
assert len(re.findall(r'https://',text))>=5
print({"svg_valid":True,"bytes":len(raw),"entries":5})
def free_submit_gate():
    x=(cli("task","get",TASK_ID).get("data") or {})
    acts=x.get("pendingActions") or []
    return x.get("submissionWindowOpen") is True and any(a.get("role")=="worker" and a.get("action")=="submit" and not a.get("requiresPayment") and (not a.get("eligibleAddress") or a.get("eligibleAddress","").lower()==AGENT) for a in acts)
if not free_submit_gate():
    print({"submitted":False,"reason":"free_submit_gate_closed"}); sys.exit(0)
rows=cli("task","submissions",TASK_ID).get("data") or []
mine=[r for r in rows if (r.get("workerAddress") or "").lower()==AGENT]
if mine:
    print({"submitted":False,"reason":"already_submitted","submission_id":mine[-1].get("id")}); sys.exit(0)
if not free_submit_gate(): print({"submitted":False,"reason":"final_gate_closed"}); sys.exit(0)
out=cli("task","submit",TASK_ID,"--file",FILE)
sid=(out.get("data") or {}).get("submissionId")
rows=cli("task","submissions",TASK_ID).get("data") or []
mine=[r for r in rows if (r.get("workerAddress") or "").lower()==AGENT]
assert mine, "submission not confirmed"
print({"submitted":True,"submission_id":sid or mine[-1].get("id"),"confirmed":True})
