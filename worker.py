"""EarnAgent deterministic worker core.
Creates verifiable work plans only for narrow task classes. It never executes
commands from remote task text and never marks work completed by itself.
"""
import re, hashlib, json

ALLOWED_KINDS={"docs_edit","text_replacement","test_update","config_edit"}

def fingerprint(candidate):
    raw=(candidate.get("url","")+"|"+candidate.get("title","")).encode()
    return hashlib.sha256(raw).hexdigest()[:24]

def classify(candidate):
    text=(candidate.get("title","")+" "+candidate.get("body","")).lower()
    if re.search(r"\b(readme|documentation|docs?|typo|spelling)\b",text):
        return "docs_edit"
    if re.search(r"\b(replace|rename|wording|text)\b",text):
        return "text_replacement"
    if re.search(r"\b(unit test|tests?|test case)\b",text):
        return "test_update"
    if re.search(r"\b(config|configuration|yaml|json)\b",text):
        return "config_edit"
    return None

def make_plan(candidate, seen_ids=None):
    seen_ids=set(seen_ids or [])
    cid=fingerprint(candidate)
    kind=classify(candidate)
    blockers=[]
    if cid in seen_ids: blockers.append("duplicate")
    if not candidate.get("eligible"): blockers.append("quality_gate_failed")
    if not candidate.get("reward_usd"): blockers.append("no_numeric_reward")
    if kind not in ALLOWED_KINDS: blockers.append("unsupported_task_kind")
    return {
      "id":cid,"kind":kind,"state":"blocked" if blockers else "planned",
      "blockers":blockers,
      "verification":["minimal_diff","acceptance_criteria_match","no_secret_changes","no_binary_changes"],
      "submission":"disabled_until_payout_and_submission_ready"
    }

if __name__=="__main__":
    print(json.dumps({"status":"ok","worker":"deterministic","allowed_kinds":sorted(ALLOWED_KINDS)}))
