#!/usr/bin/env python3
"""Autonomous Agent Souk seller: paid live URL intelligence briefs."""
import json, os, re, socket, ipaddress, urllib.request, urllib.parse
from pathlib import Path

STATE=Path("data/agentsouk_state.json")
LOG=Path("data/agentsouk_run.json")
BASE="https://api.agentsouk.dev"
NAME="EarnAgent URL Intelligence"
PRICE=450000  # 0.45 USDC

def fetch(url, max_bytes=120000):
    p=urllib.parse.urlparse(url)
    if p.scheme not in ("http","https") or not p.hostname: raise ValueError("Only public http(s) URLs are allowed")
    host=p.hostname
    try:
        ips=socket.getaddrinfo(host,None)
        for item in ips:
            ip=ipaddress.ip_address(item[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise ValueError("Private/local network URL rejected")
    except socket.gaierror:
        raise ValueError("Host could not be resolved")
    req=urllib.request.Request(url,headers={"User-Agent":"EarnAgent-URL-Intelligence/1.0","Accept":"text/html,text/plain,application/json"})
    with urllib.request.urlopen(req,timeout=18) as r:
        raw=r.read(max_bytes+1)
        ct=r.headers.get("content-type","")
    if len(raw)>max_bytes: raw=raw[:max_bytes]
    text=raw.decode("utf-8","replace")
    text=re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<noscript[\s\S]*?</noscript>"," ",text,flags=re.I)
    text=re.sub(r"<[^>]+>"," ",text)
    text=re.sub(r"\\s+"," ",text).strip()
    return {"url":url,"content_type":ct,"text":text[:90000]}

def main():
    out={"enabled":False,"reason":"","jobs_seen":0,"jobs_delivered":0,"revenue_verified_usd":0.0}
    key=os.getenv("AGENTSOUK_API_KEY")
    if not key and STATE.exists():
        try: key=json.loads(STATE.read_text()).get("api_key")
        except Exception: key=None
    wallet=os.getenv("EARNAGENT_AGENT_WALLET_ADDRESS") or os.getenv("TASKMARKET_WALLET_ADDRESS")
    private=os.getenv("EARNAGENT_AGENT_PRIVATE_KEY") or os.getenv("TASKMARKET_AGENT_PRIVATE_KEY")
    if private and not wallet:
        try:
            from eth_account import Account
            wallet=Account.from_key(private).address
        except Exception:
            wallet=None
    try:
        from agentsouk import AgentSouk, wallet_message
        if not key:
            reg=AgentSouk.register(name="EarnAgent",description="Autonomous paid public-web intelligence service",capabilities=["research","web","comparison"])
            key=reg["api_keys"]["live"]
            STATE.parent.mkdir(parents=True,exist_ok=True)
            STATE.write_text(json.dumps({"api_key":key,"agent_id":reg["agent"]["id"]}),encoding="utf-8")
        elif not STATE.exists():
            STATE.parent.mkdir(parents=True,exist_ok=True)
            STATE.write_text(json.dumps({"api_key":key}),encoding="utf-8")
        from eth_account import Account
        from eth_account.messages import encode_defunct
        aw=AgentSouk(api_key=key, base_url=BASE)
        me=aw.agents.me()
        if wallet and private and not me.get("wallet_address"):
            sig=Account.sign_message(encode_defunct(text=wallet_message(me["id"],wallet)),private_key=private).signature.hex()
            aw.agents.set_wallet_address(wallet,sig)
        mine=aw.listings.mine()
        listings=mine.get("data",mine) if isinstance(mine,dict) else mine
        listings=listings if isinstance(listings,list) else []
        listing=next((x for x in listings if x.get("title")==NAME),None)
        if not listing:
            listing=aw.listings.create(
                title=NAME,
                description="Fetch up to five public URLs and return a grounded comparison/decision brief. Live retrieval, key claims, differences, risks and actionable takeaways. No credentials, private pages or local-network targets.",
                category="research",
                price=PRICE,
                input_schema={"type":"object","required":["urls","objective"],"properties":{
                    "urls":{"type":"array","minItems":1,"maxItems":5,"items":{"type":"string","format":"uri"}},
                    "objective":{"type":"string","minLength":10,"maxLength":1200}
                }},
                output_schema={"type":"object","required":["objective","sources","findings","risks","recommendation"],"properties":{
                    "objective":{"type":"string"},"sources":{"type":"array"},"findings":{"type":"array"},
                    "risks":{"type":"array"},"recommendation":{"type":"string"}}
                },
                answer_within_seconds=180,
                max_revisions=1
            )
        listing_id=listing.get("id")
        jobs=aw.jobs.list(role="seller")
        rows=jobs.get("data",jobs) if isinstance(jobs,dict) else jobs
        rows=rows if isinstance(rows,list) else []
        out.update({"enabled":True,"agent_id":me.get("id"),"listing_id":listing_id,"jobs_seen":len(rows)})
        for job in rows[:8]:
            status=str(job.get("status",""))
            if status in ("completed","cancelled","expired","declined","disputed","resolved"): continue
            jid=job.get("id")
            try:
                if status in ("pending","requested","created","awaiting_acceptance"):
                    aw.jobs.accept(jid)
                    job=aw.jobs.get(jid)
                    status=str(job.get("status",""))
                inp=job.get("input") or {}
                urls=inp.get("urls") if isinstance(inp,dict) else None
                objective=inp.get("objective") if isinstance(inp,dict) else None
                if status not in ("accepted","in_progress","awaiting_delivery","delivery_due") or not isinstance(urls,list) or not objective: continue
                if len(urls)>5: raise ValueError("Maximum five URLs")
                pages=[fetch(u) for u in urls]
                # Use the existing OpenAI key only for synthesis; no external credentials are accepted from buyers.
                from openai import OpenAI
                client=OpenAI(api_key=os.environ["OPENAI_API_KEY"])
                material="\n\n".join("SOURCE "+str(i+1)+"\nURL: "+p["url"]+"\n"+p["text"] for i,p in enumerate(pages))
                prompt=("Create a concise, evidence-grounded comparison brief. Objective: "+objective+
                        "\nUse ONLY the supplied source material. Do not invent facts. Return JSON with keys "
                        "objective,sources,findings,risks,recommendation. Each finding must cite source numbers.\n\n"+material)
                resp=client.responses.create(model=os.getenv("EARNAGENT_MODEL","gpt-6-luna"),input=prompt)
                txt=resp.output_text
                try: result=json.loads(txt)
                except Exception: result={"objective":objective,"sources":[p["url"] for p in pages],"findings":[txt],"risks":[],"recommendation":"See findings."}
                aw.jobs.deliver(jid,result,message="Automated live URL intelligence brief.",preview={"sources":[p["url"] for p in pages],"status":"ready"})
                out["jobs_delivered"]+=1
            except Exception as e:
                out.setdefault("errors",[]).append({"job_id":jid,"error":str(e)[:240]})
        # Revenue is reported only from verified settlements.
        try:
            settlements=aw.payments.settlements()
            vals=settlements.get("data",settlements) if isinstance(settlements,dict) else []
            total=0
            for s in vals if isinstance(vals,list) else []:
                if s.get("seller_agent_id")==me.get("id") and s.get("status") in ("settled","verified","confirmed"):
                    total += float(s.get("amount_usd") or s.get("amount") or 0)/1000000 if float(s.get("amount_usd") or 0)==0 else float(s.get("amount_usd") or 0)
            out["revenue_verified_usd"]=round(total,6)
        except Exception: pass
    except Exception as e:
        out["reason"]=str(e)[:500]
    LOG.parent.mkdir(parents=True,exist_ok=True); LOG.write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__": main()
