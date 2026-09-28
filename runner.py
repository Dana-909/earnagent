"""EarnAgent end-to-end dry-run orchestrator.
Live network submission remains disabled until provider + payout are configured.
"""
from worker import make_plan
from verifier import verify
from submitter import prepare,may_submit
from ledger import transition

def dry_run(candidate):
    plan=make_plan(candidate)
    if plan["state"]!="planned": return {"stage":"worker","ok":False,"detail":plan}
    record={"id":plan["id"],"state":"discovered","reward_usd":candidate.get("reward_usd",0)}
    record=transition(record,"planned")
    # Synthetic product tests orchestration only; it is never counted as external completion.
    product={"files":[{"path":"README.md","bytes":64}],"acceptance_criteria_checked":True,"tests_passed":True}
    record=transition(record,"produced")
    v=verify(product)
    if v["verified"]: record=transition(record,"verified")
    env=prepare({"id":plan["id"],"product_hash":"dry-run"},v,
                {"configured":False},{"automation_allowed":False,"submission_api_ready":False})
    return {"stage":"submission_gate","ok":v["verified"] and not may_submit(env),
            "record":record,"verification":v,"submission":env,
            "live_submission_attempted":False,"verified_revenue_usd":0}

if __name__=="__main__":
    demo={"title":"Fix README typo","body":"Update documentation typo","eligible":True,"reward_usd":25,"url":"https://example.invalid/task"}
    result=dry_run(demo)
    assert result["ok"] and result["verified_revenue_usd"]==0 and not result["live_submission_attempted"]
    print(result)
