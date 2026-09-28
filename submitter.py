"""EarnAgent submission gate.
This module prepares an auditable submission envelope. Network submission stays
fail-closed until payout route + provider permission + verified work are green.
"""
import hashlib, json

def submission_id(task_id, product_hash):
    return hashlib.sha256((task_id+"|"+product_hash).encode()).hexdigest()[:24]

def prepare(task, verification, payout, provider):
    blockers=[]
    if not verification.get("verified"): blockers.append("work_not_verified")
    if not payout.get("configured"): blockers.append("payout_not_configured")
    if not provider.get("automation_allowed"): blockers.append("provider_automation_not_verified")
    if not provider.get("submission_api_ready"): blockers.append("submission_channel_not_ready")
    product_hash=task.get("product_hash","missing")
    sid=submission_id(task.get("id","missing"),product_hash)
    return {"submission_id":sid,"state":"ready" if not blockers else "blocked",
            "blockers":blockers,"idempotency_key":sid,
            "external_submission_url":None,"payment_status":"unpaid"}

def may_submit(envelope):
    return envelope.get("state")=="ready" and not envelope.get("blockers")

if __name__=="__main__":
    print(json.dumps(prepare({"id":"demo","product_hash":"x"},{"verified":True},
      {"configured":False},{"automation_allowed":False,"submission_api_ready":False})))
