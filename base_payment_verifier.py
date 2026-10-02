import json, os, time, urllib.request
from pathlib import Path

RPC=os.getenv("EARNAGENT_BASE_RPC","https://mainnet.base.org")
WALLET=(os.getenv("EARNAGENT_SALES_WALLET_ADDRESS") or os.getenv("TASKMARKET_WALLET_ADDRESS") or "0x948B78F80ba73E846B27171f31E3609b0e399701").lower()
USDC="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aeb2a5b4e5"
PRODUCT_PRICES={"freelancer-invoice-kit":7.0,"small-business-kpi-dashboard":9.0,"content-calendar-kit":5.0,"job-application-tracker":4.0,"svg-social-icon-pack":6.0,"project-planning-kit":8.0}
STATE=Path("data/base_payments.json")

def rpc(method,params):
    req=urllib.request.Request(RPC,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as r: out=json.loads(r.read().decode())
    if out.get("error"): raise RuntimeError(str(out["error"])[:300])
    return out.get("result")

def main():
    try: state=json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception: state={}
    seen=set(state.get("tx_hashes",[]))
    latest=int(rpc("eth_blockNumber",[]),16)
    start=int(state.get("last_block",max(0,latest-50000)))+1
    if start>latest: start=latest
    topic_to="0x"+"0"*24+WALLET[2:]
    transfers=[]
    for a in range(start,latest+1,10000):
        b=min(latest,a+9999)
        logs=rpc("eth_getLogs",[{"address":USDC,"fromBlock":hex(a),"toBlock":hex(b),"topics":[TRANSFER,None,topic_to]}]) or []
        for log in logs:
            tx=log.get("transactionHash")
            if not tx or tx in seen: continue
            raw=int((log.get("data") or "0x0")[2:],16)
            amount=raw/1_000_000
            product=next((slug for slug,price in PRODUCT_PRICES.items() if abs(amount-price)<0.000001),None)
            if product:
                transfers.append({"tx_hash":tx,"product":product,"amount_usd":amount,"block":int(log.get("blockNumber","0x0"),16),"verified":True})
            seen.add(tx)
    state={"last_block":latest,"tx_hashes":list(seen)[-5000:],"verified_transfers":state.get("verified_transfers",[])+transfers}
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state,ensure_ascii=False,separators=(",",":")))
    revenue=round(sum(float(x["amount_usd"]) for x in state["verified_transfers"]),2)
    print(json.dumps({"status":"verified","wallet":WALLET,"latest_block":latest,"new_sales":len(transfers),"verified_sales":len(state["verified_transfers"]),"verified_revenue_usd":revenue,"new_transfers":transfers},ensure_ascii=False))

if __name__=="__main__": main()
