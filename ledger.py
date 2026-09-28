"""Append-only logical ledger helpers for EarnAgent.
State transitions are monotonic: advertised rewards never become revenue.
"""
VALID=("discovered","planned","produced","verified","submitted","accepted","paid","withdrawable","withdrawn")
RANK={s:i for i,s in enumerate(VALID)}

def transition(record,new_state,external_evidence=None):
    old=record.get("state","discovered")
    if new_state not in RANK or old not in RANK: raise ValueError("unknown_state")
    if RANK[new_state] < RANK[old]: raise ValueError("state_regression")
    if new_state in ("accepted","paid","withdrawable","withdrawn") and not external_evidence:
        raise ValueError("external_evidence_required")
    out=dict(record); out["state"]=new_state
    if external_evidence: out.setdefault("evidence",[]).append(external_evidence)
    if new_state=="paid":
        amount=float(external_evidence.get("amount_usd",0))
        if amount<=0: raise ValueError("positive_payment_required")
        out["verified_revenue_usd"]=amount
    return out

def verified_total(records):
    return round(sum(float(r.get("verified_revenue_usd",0)) for r in records if RANK.get(r.get("state"),-1)>=RANK["paid"]),2)
