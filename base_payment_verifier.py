import json,os,urllib.request
from pathlib import Path
NETWORKS={
 "base":{"rpc":"https://mainnet.base.org","usdc":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
 "arbitrum":{"rpc":"https://arb1.arbitrum.io/rpc","usdc":"0xaf88d065e77c8cC2239327C5EDb3A432268e5831"},
 "polygon":{"rpc":"https://polygon-rpc.com","usdc":"0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
 "optimism":{"rpc":"https://mainnet.optimism.io","usdc":"0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"},
}
WALLET=(os.getenv("EARNAGENT_SALES_WALLET_ADDRESS") or os.getenv("TASKMARKET_WALLET_ADDRESS") or "0x948B78F80ba73E846B27171f31E3609b0e399701").lower()
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aeb2a5b4e5"
PRICES={"freelancer-invoice-kit":7.0,"small-business-kpi-dashboard":9.0,"content-calendar-kit":5.0,"job-application-tracker":4.0,"svg-social-icon-pack":6.0,"project-planning-kit":8.0}
STATE=Path("data/base_payments.json")
def call(url,method,params):
 req=urllib.request.Request(url,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=20) as r: return json.loads(r.read().decode()).get("result")
def main():
 state=json.loads(STATE.read_text()) if STATE.exists() else {}
 seen=set(state.get("tx_keys",[])); transfers=[]; blocks=dict(state.get("last_blocks",{}))
 for name,cfg in NETWORKS.items():
  try:
   latest=int(call(cfg["rpc"],"eth_blockNumber",[]),16); start=int(blocks.get(name,max(0,latest-50000)))+1
   if start>latest: start=latest
   topic="0x"+"0"*24+WALLET[2:]
   for a in range(start,latest+1,10000):
    b=min(latest,a+9999); logs=call(cfg["rpc"],"eth_getLogs",[{"address":cfg["usdc"],"fromBlock":hex(a),"toBlock":hex(b),"topics":[TRANSFER,None,topic]}]) or []
    for log in logs:
     tx=log.get("transactionHash"); key=name+":"+str(tx)
     if not tx or key in seen: continue
     amount=int((log.get("data") or "0x0")[2:],16)/1000000; product=next((p for p,v in PRICES.items() if abs(amount-v)<0.000001),None)
     if product: transfers.append({"tx_hash":tx,"network":name,"product":product,"amount_usd":amount,"block":int(log.get("blockNumber","0x0"),16),"verified":True,"status":"paid_unclaimed"})
     seen.add(key)
   blocks[name]=latest
  except Exception as e: print(json.dumps({"network":name,"error":str(e)[:200]}))
 old=state.get("verified_transfers",[]); known={(x.get("network"),x.get("tx_hash")) for x in old}
 state={"last_blocks":blocks,"tx_keys":list(seen)[-10000:],"verified_transfers":old+[x for x in transfers if (x["network"],x["tx_hash"]) not in known]}
 STATE.parent.mkdir(exist_ok=True); STATE.write_text(json.dumps(state,separators=(",",":")))
 print(json.dumps({"networks":list(NETWORKS),"new_sales":len(transfers),"verified_sales":len(state["verified_transfers"]),"verified_revenue_usd":round(sum(x["amount_usd"] for x in state["verified_transfers"]),2)}))
 if __name__=="__main__": main()
