import json, os, hashlib, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path("store"); PRODUCTS=ROOT/"products"; STATE=Path("data/sales_engine.json")
PRODUCTS.mkdir(parents=True,exist_ok=True); STATE.parent.mkdir(exist_ok=True)
WALLET=os.getenv("TASKMARKET_WALLET_ADDRESS") or "0x948B78F80ba73E846B27171f31E3609b0e399701"
BASE_USDC="USDC on Base"
PRODUCTS_PLAN=[
 {"slug":"marketplace-profit-leak-audit","title":"Instant Profit Leak Audit","price":9.00,"kind":"html","pitch":"A practical seller-ops audit that estimates margin leakage across fees, returns, ads, discounts and manual work."},
 {"slug":"marketplace-ops-dashboard","title":"Marketplace Ops Dashboard","price":49.00,"kind":"html","pitch":"A browser-based operating dashboard for orders, revenue, fees, ad spend, returns, margin and weekly priorities."},
 {"slug":"ai-listing-optimization-kit","title":"AI Listing Optimization Kit","price":39.00,"kind":"md","pitch":"A repeatable workflow for improving marketplace titles, descriptions, attributes and creative briefs with measurable tests."},
 {"slug":"seller-cashflow-planner","title":"Seller Cashflow Planner","price":19.00,"kind":"html","pitch":"A lightweight cashflow planner for marketplace sellers that models payouts, fees, ad spend and upcoming obligations."},
 {"slug":"ecommerce-kpi-review-kit","title":"Ecommerce KPI Review Kit","price":24.00,"kind":"md","pitch":"A weekly operating review system for conversion, contribution margin, returns, inventory and channel performance."},
 {"slug":"marketplace-automation-blueprint","title":"Marketplace Automation Blueprint","price":79.00,"kind":"md","pitch":"A prioritized blueprint for reducing repetitive marketplace operations with AI and workflow automation."},
 {"slug":"marketplace-profit-rescue-report","title":"Instant Profit Rescue Report","price":9.00,"kind":"html","pitch":"An interactive profit-rescue report generator that turns seller metrics into a prioritized action plan and printable management report."},
]

def write_product(p):
    path=PRODUCTS/(p["slug"]+"."+p["kind"])
    slug=p["slug"]
    if slug=="marketplace-profit-leak-audit":
        body="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Marketplace Profit Leak Audit Kit</title>
<style>body{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}main{max-width:920px;margin:30px auto;padding:28px;background:#fff;border-radius:18px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}label{display:block}input,button{font:inherit;padding:11px;margin:5px 0;box-sizing:border-box}input{width:100%}button{cursor:pointer}.result{font-size:1.2rem;font-weight:700;padding:15px;background:#eef5f8;border-radius:12px}@media(max-width:650px){.grid{grid-template-columns:1fr}}</style></head><body><main><h1>Marketplace Profit Leak Audit Kit</h1><p>Quantify the biggest operational leaks before spending more time or ad budget.</p>
<div class="grid"><label>Revenue ($)<input id="rev" type="number" value="5000"></label><label>Marketplace fees ($)<input id="fees" type="number" value="750"></label><label>Ads ($)<input id="ads" type="number" value="500"></label><label>Returns/refunds ($)<input id="ret" type="number" value="200"></label><label>Discounts ($)<input id="disc" type="number" value="100"></label><label>Manual hours<input id="hours" type="number" value="20"></label><label>Value per hour ($)<input id="rate" type="number" value="25"></label></div>
<button onclick="audit()">Run audit</button><p id="out" class="result">Enter your numbers and run the audit.</p><h2>Action queue</h2><ol id="queue"></ol><hr><small>Runs locally in your browser; inputs are not uploaded.</small></main><script>function audit(){const x={Fees:+fees.value,Ads:+ads.value,Returns:+ret.value,Discounts:+disc.value,"Manual work":+hours.value*+rate.value};const rev=+document.getElementById("rev").value;const rows=Object.entries(x).sort((a,b)=>b[1]-a[1]);const leaks=rows.reduce((a,b)=>a+b[1],0);out.textContent="Listed leakage: $"+leaks.toFixed(2)+" · contribution after listed leakage: $"+(rev-leaks).toFixed(2)+" · leakage rate: "+(rev?100*leaks/rev:0).toFixed(1)+"%";queue.innerHTML=rows.map((r,i)=>"<li><b>"+r[0]+"</b>: $"+r[1].toFixed(2)+" — "+(i===0?"fix this first":"measure and reduce")+"</li>").join("")}</script></body></html>"""
    elif slug=="marketplace-ops-dashboard":
        body="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Marketplace Ops Dashboard</title><style>body{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}main{max-width:1000px;margin:30px auto;padding:28px;background:#fff;border-radius:18px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{padding:16px;background:#eef5f8;border-radius:12px}input,button{font:inherit;padding:10px;width:100%;box-sizing:border-box;margin:5px 0}button{cursor:pointer}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head><body><main><h1>Marketplace Ops Dashboard</h1><p>One-page weekly snapshot for revenue, contribution and operating workload.</p><div class="grid"><label>Orders<input id="orders" type="number" value="100"></label><label>Revenue ($)<input id="revenue" type="number" value="5000"></label><label>Fees ($)<input id="fees" type="number" value="750"></label><label>Ads ($)<input id="ads" type="number" value="500"></label><label>Returns ($)<input id="returns" type="number" value="200"></label><label>Manual hours<input id="hours" type="number" value="20"></label></div><button onclick="run()">Update dashboard</button><div class="grid"><div class="card"><b>AOV</b><div id="aov">—</div></div><div class="card"><b>Contribution</b><div id="margin">—</div></div><div class="card"><b>Manual hours/order</b><div id="hpo">—</div></div></div><h2>Weekly priorities</h2><textarea id="notes" rows="6" style="width:100%;box-sizing:border-box" placeholder="Top bottleneck, owner, next action, deadline..."></textarea><button onclick="localStorage.setItem('earnagent_dashboard_notes',notes.value)">Save notes locally</button><hr><small>No account or upload required.</small></main><script>notes.value=localStorage.getItem("earnagent_dashboard_notes")||"";function run(){const o=+orders.value,r=+revenue.value,f=+fees.value,a=+ads.value,ret=+returns.value,h=+hours.value;aov.textContent="$"+(o?r/o:0).toFixed(2);margin.textContent="$"+(r-f-a-ret).toFixed(2)+" ("+(r?100*(r-f-a-ret)/r:0).toFixed(1)+"%)";hpo.textContent=(o?h/o:0).toFixed(2)}</script></body></html>"""
    elif slug=="marketplace-profit-rescue-report":
        body="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Marketplace Profit Rescue Report</title><style>body{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}main{max-width:900px;margin:30px auto;padding:28px;background:#fff;border-radius:18px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}input,button{font:inherit;padding:11px;width:100%;box-sizing:border-box;margin:5px 0}button{cursor:pointer}.report{padding:20px;background:#eef5f8;border-radius:12px}.report h2{margin-top:0}@media(max-width:650px){.grid{grid-template-columns:1fr}}@media print{button{display:none}body{background:#fff}main{margin:0}}</style></head><body><main><h1>Marketplace Profit Rescue Report</h1><p>Turn a seller's core numbers into a prioritized profit-rescue plan.</p><div class="grid"><label>Revenue ($)<input id="rev" type="number" value="25000"></label><label>Product cost ($)<input id="cost" type="number" value="10000"></label><label>Marketplace fees ($)<input id="fees" type="number" value="3750"></label><label>Ads ($)<input id="ads" type="number" value="2500"></label><label>Returns ($)<input id="ret" type="number" value="750"></label><label>Discounts ($)<input id="disc" type="number" value="500"></label><label>Manual hours/month<input id="hours" type="number" value="60"></label><label>Hourly value ($)<input id="rate" type="number" value="30"></label></div><button onclick="build()">Generate report</button><button onclick="window.print()">Print / Save PDF</button><section id="report" class="report"><h2>Report</h2><p>Generate the report to see the plan.</p></section><hr><small>Runs locally in the browser. No seller data is uploaded.</small></main><script>function build(){const r=+rev.value,c=+cost.value,f=+fees.value,a=+ads.value,t=+ret.value,d=+disc.value,h=+hours.value,v=+rate.value;const manual=h*v;const contribution=r-c-f-a-t-d-manual;const leaks=[["Marketplace fees",f],["Ads",a],["Returns",t],["Discounts",d],["Manual work",manual]].sort((x,y)=>y[1]-x[1]);report.innerHTML="<h2>Profit Rescue Report</h2><p><b>Contribution after listed costs:</b> $"+contribution.toFixed(2)+" ("+(r?100*contribution/r:0).toFixed(1)+"%)</p><h3>Priority actions</h3><ol>"+leaks.map(x=>"<li><b>"+x[0]+"</b>: $"+x[1].toFixed(2)+" — quantify one reduction experiment this month.</li>").join("")+"</ol><p><b>Largest visible lever:</b> "+leaks[0][0]+" ($"+leaks[0][1].toFixed(2)+").</p><p><b>Next review:</b> repeat the same report after the next operating cycle and compare contribution, not revenue alone.</p>"} </script></body></html>""";
    elif slug=="seller-cashflow-planner":
        body="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Seller Cashflow Planner</title><style>body{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}main{max-width:800px;margin:30px auto;padding:28px;background:#fff;border-radius:18px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}input,button{font:inherit;padding:11px;width:100%;box-sizing:border-box;margin:5px 0}button{cursor:pointer}.result{padding:16px;background:#eef5f8;border-radius:12px;font-weight:700}@media(max-width:650px){.grid{grid-template-columns:1fr}}</style></head><body><main><h1>Seller Cashflow Planner</h1><p>Model the next payout cycle before committing cash to ads, inventory or bills.</p><div class="grid"><label>Next payout ($)<input id="p" type="number" value="5000"></label><label>Marketplace fees ($)<input id="f" type="number" value="750"></label><label>Ads ($)<input id="a" type="number" value="500"></label><label>Inventory/bills ($)<input id="b" type="number" value="800"></label><label>Cash on hand ($)<input id="c" type="number" value="3000"></label><label>Safety buffer ($)<input id="s" type="number" value="1500"></label></div><button onclick="calc()">Plan cycle</button><p id="out" class="result"></p><script>function calc(){const net=+p.value-+f.value-+a.value-+b.value;const cash=+c.value+net;out.textContent="Net cycle: $"+net.toFixed(2)+" · projected cash: $"+cash.toFixed(2)+" · buffer "+(cash-+s.value>=0?"OK":"AT RISK")+" by $"+Math.abs(cash-+s.value).toFixed(2)}</script></main></body></html>"""
    elif p["kind"]=="md":
        templates={
"ai-listing-optimization-kit":"# AI Listing Optimization Kit\n\n## Goal\nImprove one listing through measurable experiments rather than endless rewriting.\n\n## Listing input\n- Product / SKU:\n- Marketplace:\n- Current title:\n- Current price:\n- Conversion rate:\n- Return rate:\n\n## Experiment matrix\n1. Title: benefit + differentiator + key attribute.\n2. First 160 characters: buyer problem + proof + use case.\n3. Attributes: remove ambiguity and fill missing structured fields.\n4. Creative brief: show product, scale, use and strongest objection.\n\n## Measurement\n- Baseline metric:\n- Variant:\n- Start/end dates:\n- Result:\n- Keep / revert:\n\n## Rule\nChange one major variable at a time and record the result.",
"ecommerce-kpi-review-kit":"# Ecommerce KPI Review Kit\n\n## Weekly scorecard\n- Revenue:\n- Orders:\n- AOV:\n- Marketplace fees:\n- Ad spend:\n- Returns/refunds:\n- Contribution after listed costs:\n- Inventory risk:\n\n## Questions\n1. Which channel produced the best contribution, not just sales?\n2. Which SKU lost margin?\n3. Which operational task consumed the most time?\n4. What single change will be tested next week?\n\n## Decision log\n- Keep:\n- Stop:\n- Test:\n- Automate:",
"marketplace-automation-blueprint":"# Marketplace Automation Blueprint\n\n## Score each process\nScore frequency 1–5, time cost 1–5, error risk 1–5, and automation feasibility 1–5.\n\nPriority = frequency × time cost × error risk × feasibility.\n\n## Candidate processes\n- Listing QA\n- Price monitoring\n- Inventory alerts\n- Order reconciliation\n- Weekly KPI reporting\n- Customer-response drafting\n- Returns triage\n\n## Automation brief\n- Trigger:\n- Input:\n- Decision:\n- Action:\n- Human approval needed:\n- Success metric:\n- Failure fallback:",
}
        body=templates.get(slug,"# "+p["title"]+"\n\n"+p["pitch"]+"\n\n## Checklist\n- [ ] Define baseline\n- [ ] Execute\n- [ ] Measure\n- [ ] Improve")
    else:
        body='''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700"><rect width="1200" height="700" fill="#f4f1ea"/><text x="60" y="100" font-family="system-ui" font-size="42" font-weight="700">EarnAgent</text><text x="60" y="165" font-family="system-ui" font-size="28">Marketplace operations toolkit</text></svg>'''
    path.write_text(body,encoding="utf-8")
    return path

def lemon_api_get(path,key):
    req=urllib.request.Request(
        "https://api.lemonsqueezy.com/v1/"+path.lstrip("/"),
        headers={"Accept":"application/vnd.api+json","Content-Type":"application/vnd.api+json","Authorization":"Bearer "+key})
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.loads(r.read().decode())

def lemon_commercial_state():
    key=os.getenv("LEMONSQUEEZY_API_KEY")
    if not key:
        return {"configured":False,"status":"not_configured","products":[],"paid_orders":[]}
    try:
        stores=lemon_api_get("stores?page[size]=100",key).get("data",[])
        products=lemon_api_get("products?page[size]=100",key).get("data",[])
        variants=lemon_api_get("variants?page[size]=100",key).get("data",[])
        orders=lemon_api_get("orders?page[size]=100&sort=-createdAt",key).get("data",[])
        store_slug=stores[0].get("attributes",{}).get("slug") if stores else None
        variant_by_product={}
        for v in variants:
            pid=str(v.get("relationships",{}).get("product",{}).get("data",{}).get("id",""))
            if pid and pid not in variant_by_product:
                variant_by_product[pid]=v.get("id")
        published=[]
        for x in products:
            a=x.get("attributes",{})
            published.append({"id":x.get("id"),"slug":a.get("slug"),"name":a.get("name"),
                              "status":a.get("status"),"buy_now_url":a.get("buy_now_url") or (("https://"+store_slug+".lemonsqueezy.com/checkout/buy/"+str(variant_by_product.get(str(x.get("id"))))) if store_slug and variant_by_product.get(str(x.get("id"))) else None),
                              "variant_id":variant_by_product.get(str(x.get("id"))),"price_cents":a.get("price")})
        paid=[]
        revenue=0.0
        for x in orders:
            a=x.get("attributes",{})
            if a.get("status")=="paid" and not a.get("refunded"):
                total=float(a.get("total_usd",a.get("total",0)) or 0)/100
                revenue+=total
                item=a.get("first_order_item") or {}
                paid.append({"id":x.get("id"),"order_number":a.get("order_number"),
                             "product_id":item.get("product_id"),"product_name":item.get("product_name"),
                             "total_usd":round(total,2),"created_at":a.get("created_at"),
                             "test_mode":bool(a.get("test_mode",False))})
        return {"configured":True,"status":"connected","stores":len(stores),
                "store_names":[x.get("attributes",{}).get("name") for x in stores],
                "published_products":published,"paid_orders":paid,
                "verified_revenue_usd":round(revenue,2),
                "live_paid_orders":sum(1 for x in paid if not x["test_mode"]),
                "test_paid_orders":sum(1 for x in paid if x["test_mode"])}
    except Exception as e:
        return {"configured":True,"status":"error","error":str(e)[:240],"products":[],"paid_orders":[]}

def render_store(products, lemon_state):
    cards=[]
    ls={x.get("slug"):x for x in lemon_state.get("published_products",[])}
    for p in products:
        hosted=ls.get(p["slug"],{})
        buy=hosted.get("buy_now_url")
        buy_html='<p><a class="cta" href="'+buy+'">Buy securely online</a></p>' if buy else ''
        usdc='<p><a class="cta secondary" href="pay.html?product='+p["slug"]+'">Pay with USDC on Base — $'+format(p["price"],".2f")+'</a></p>'
        cards.append('<article><h2>'+p["title"]+'</h2><p>'+p["pitch"]+'</p><strong>$'+format(p["price"],".2f")+
                     '</strong><p><a href="products/'+p["slug"]+'.'+p["kind"]+'">Preview / use the tool</a></p>'+buy_html+usdc+
                     '<small>Only verified payment/order events count as sales.</small></article>')
    html='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Marketplace Seller Profit Tools — EarnAgent</title><meta name="description" content="Practical marketplace profit, operations, cashflow and automation tools for ecommerce sellers."><style>body{font:16px system-ui;margin:0;background:#101820;color:#f5f1e8}main{max-width:1050px;margin:auto;padding:30px}article{background:#18252e;padding:22px;margin:16px 0;border-radius:16px}a{color:#b9e4ff}.cta{display:inline-block;padding:11px 14px;background:#d8f3dc;color:#10201b;border-radius:9px;text-decoration:none;margin:5px 0}.secondary{background:#b9e4ff}small{display:block;opacity:.8;margin-top:12px}</style></head><body><main><h1>Marketplace Seller Profit & Automation Tools</h1><p>Free calculators help you find a leak. Paid tools turn the finding into a repeatable operating workflow.</p>'''+''.join(cards)+'''<hr><p><a href="free/marketplace-profit-checker.html">Free profit-leak checker</a> · <a href="free/seller-kpi-checker.html">Free KPI checker</a> · <a href="free/cashflow-checker.html">Free cashflow checker</a></p></main></body></html>'''
    (ROOT/"index.html").write_text(html,encoding="utf-8")

def ai_product_variant(seed):
    key=os.getenv("OPENAI_API_KEY")
    if not key: return None
    try:
        payload={"model":os.getenv("EARNAGENT_MODEL","gpt-5.6-luna"),"input":[{"role":"system","content":"Return ONLY JSON with slug,title,price,kind,pitch,content. Create one original safe digital product variant. Allowed kind: html, md, svg. No external URLs, accounts, credentials, payments, spam, impersonation or copyrighted copying. Price 4-29 USD."},{"role":"user","content":json.dumps(seed,ensure_ascii=False)}]}
        req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=45) as r: out=json.loads(r.read().decode())
        p=json.loads(out.get("output_text","").strip())
        if p.get("kind") not in ("html","md","svg") or not p.get("slug") or not p.get("title") or not p.get("pitch") or not p.get("content"): return None
        p["price"]=max(4.0,min(29.0,float(p.get("price",7))))
        low=p["content"].lower()
        if "http://" in low or "https://" in low or "<iframe" in low or "<foreignobject" in low or len(p["content"].encode())>500000: return None
        return p
    except Exception: return None

def load_verified_sales():
    """Merge only real, verified sales from enabled payment rails."""
    try:
        data=json.loads(STATE.read_text()) if STATE.exists() else {}
        by_name={}
        def add(name, amount):
            if not name: return
            by_name.setdefault(name,{"sales":0,"revenue":0.0})
            by_name[name]["sales"]+=1
            by_name[name]["revenue"]+=float(amount or 0)
        for o in data.get("lemon_squeezy",{}).get("paid_orders",[]):
            if not o.get("test_mode"): add(o.get("product_name"),o.get("total_usd",0))
        for t in data.get("base_payments",{}).get("verified_transfers",[]):
            if t.get("verified"):
                p=next((x for x in PRODUCTS_PLAN if x["slug"]==t.get("product")),None)
                add(p["title"] if p else t.get("product"),t.get("amount_usd",0))
        return by_name
    except Exception:
        return {}

def choose_catalog_plan():
    base=list(PRODUCTS_PLAN)
    sales=load_verified_sales()
    for p in base:
        m=sales.get(p["title"],{})
        p["verified_sales"]=m.get("sales",0)
        p["verified_revenue_usd"]=round(m.get("revenue",0.0),2)
    winners=[p for p in base if p["verified_revenue_usd"]>0]
    if winners:
        seed=max(winners,key=lambda p:p["verified_revenue_usd"])
        slug=seed["slug"]+"-advanced"
        if not any(p["slug"]==slug for p in base):
            base.append({"slug":slug,"title":seed["title"]+" Advanced Pack","price":round(max(seed["price"]*1.5,7),2),"kind":seed["kind"],"pitch":"Expanded version of the proven "+seed["title"]+" with additional workflows and practical examples."})
        ai=ai_product_variant(seed)
        if ai:
            ai["slug"]=seed["slug"]+"-"+ai["slug"].strip("-")
            if not any(p["slug"]==ai["slug"] for p in base): base.append(ai)
    return base

def render_direct_checkout(products):
    wallet=WALLET
    prices={p["slug"]:float(p["price"]) for p in products}
    labels={p["slug"]:p["title"] for p in products}
    contracts={"base":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913","arbitrum":"0xaf88d065e77c8cC2239327C5EDb3A432268e5831","polygon":"0x3c499c542cef5e3811e1192ce70d8cc03d5c3359","optimism":"0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"}
    networks={"base":{"label":"Base","chain_id":8453,"rpc":"https://mainnet.base.org","explorer":"https://basescan.org/tx/"},"arbitrum":{"label":"Arbitrum One","chain_id":42161,"rpc":"https://arb1.arbitrum.io/rpc","explorer":"https://arbiscan.io/tx/"},"polygon":{"label":"Polygon PoS","chain_id":137,"rpc":"https://polygon-rpc.com","explorer":"https://polygonscan.com/tx/"},"optimism":{"label":"Optimism","chain_id":10,"rpc":"https://mainnet.optimism.io","explorer":"https://optimistic.etherscan.io/tx/"}}
    data=json.dumps({"prices":prices,"labels":labels,"contracts":contracts,"networks":networks,"wallet":wallet},ensure_ascii=False)
    html="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EarnAgent — USDC checkout</title>
<style>body{font:16px system-ui,sans-serif;margin:0;background:#101820;color:#f5f1e8}main{max-width:820px;margin:auto;padding:28px}.card{background:#18252e;padding:22px;border-radius:16px;margin:16px 0}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}select,input{font:inherit;padding:11px;width:100%;box-sizing:border-box}code{display:block;overflow-wrap:anywhere;padding:12px;background:#24333d;border-radius:8px}.cta{display:inline-block;padding:11px 14px;background:#d8f3dc;color:#10201b;border-radius:9px;text-decoration:none;border:0;cursor:pointer;margin-top:8px}.status{padding:14px;border-radius:10px;margin-top:12px;background:#24333d}small{opacity:.82}@media(max-width:650px){.row{grid-template-columns:1fr}}</style></head>
<body><main><h1>EarnAgent checkout</h1><div class="card"><div class="row"><label>Product<select id="product"></select></label><label>Network<select id="network"></select></label></div>
<p>Exact price: <b id="amount">—</b> USDC</p><p>Native USDC contract:</p><code id="contract"></code><p>Recipient wallet:</p><code id="wallet"></code><button class="cta" id="copy">Copy wallet</button>
<p><small>Send the exact USDC amount on the selected network. A sale is counted only when the transaction matches the selected product, native USDC contract, recipient and network.</small></p>
<hr><h3>Already paid?</h3><input id="tx" placeholder="Paste transaction hash (0x…)" autocomplete="off"><button class="cta" id="verify">Verify payment</button><div id="out" class="status">Waiting for transaction hash.</div></div><p><a href="index.html" style="color:#b9e4ff">Back to store</a></p>
<script>
const catalog=CATALOG, qs=new URLSearchParams(location.search), productEl=document.getElementById("product"), networkEl=document.getElementById("network");
Object.entries(catalog.labels).forEach(([k,v])=>{const o=document.createElement("option");o.value=k;o.textContent=v+" — $"+Number(catalog.prices[k]).toFixed(2);productEl.appendChild(o)});
Object.entries(catalog.networks).forEach(([k,v])=>{const o=document.createElement("option");o.value=k;o.textContent=v.label+" (chain "+v.chain_id+")";networkEl.appendChild(o)});
productEl.value=catalog.prices[qs.get("product")]!=null?qs.get("product"):Object.keys(catalog.prices)[0];networkEl.value=catalog.networks[qs.get("network")]?qs.get("network"):"base";
function render(){const p=productEl.value,n=networkEl.value;amount.textContent=Number(catalog.prices[p]).toFixed(2);contract.textContent=catalog.contracts[n];wallet.textContent=catalog.wallet;history.replaceState(null,"","pay.html?product="+encodeURIComponent(p)+"&network="+encodeURIComponent(n))}
productEl.onchange=render;networkEl.onchange=render;copy.onclick=()=>navigator.clipboard&&navigator.clipboard.writeText(catalog.wallet);
async function rpc(url,method,params){const r=await fetch(url,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({jsonrpc:"2.0",id:1,method,params})});if(!r.ok)throw Error("RPC unavailable");const j=await r.json();return j.result}
verify.onclick=async()=>{const hash=tx.value.trim(),p=productEl.value,n=networkEl.value;if(!/^0x[0-9a-fA-F]{64}$/.test(hash)){out.textContent="Enter a valid transaction hash.";return}out.textContent="Checking the transaction…";try{const rec=await rpc(catalog.networks[n].rpc,"eth_getTransactionReceipt",[hash]);if(!rec||!rec.logs)throw Error("Transaction not found yet.");const topic="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55aeb2a5b4e5";const recipient=catalog.wallet.toLowerCase().replace("0x","").padStart(64,"0");const expected=Math.round(Number(catalog.prices[p])*1e6).toString(16).padStart(64,"0");const ok=rec.logs.some(x=>x.address.toLowerCase()===catalog.contracts[n].toLowerCase()&&x.topics&&x.topics[0].toLowerCase()===topic&&x.topics[2]&&x.topics[2].slice(-64).toLowerCase()===recipient&&BigInt(x.data)===BigInt("0x"+expected));if(!ok)throw Error("No exact matching USDC transfer found.");out.innerHTML='<b>Payment verified on-chain.</b><br><a href="'+catalog.networks[n].explorer+hash+'" target="_blank" rel="noopener">View transaction</a><br><small>EarnAgent's server-side verifier will count the sale on its next cycle.</small>'}catch(e){out.textContent=e.message||"Verification failed."}};
render();
</script></main></body></html>"""
    (ROOT/"pay.html").write_text(html.replace("CATALOG",data),encoding="utf-8")


def render_discovery_files(products):
    """Build one sitemap from the complete generated acquisition surface."""
    (ROOT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://dana-909.github.io/earnagent/store/sitemap.xml\n",encoding="utf-8")
    urls=["","pay.html"]+[f"products/{p['slug']}.{p['kind']}" for p in products]
    urls += [
        "free/marketplace-profit-checker.html","free/seller-kpi-checker.html","free/cashflow-checker.html",
        "free/cross-platform-profit-checker.html","niches/marketplace-sellers.html",
        "guides/marketplace-profit-leak-audit.html","guides/seller-margin-calculator.html",
        "guides/seller-ops-dashboard.html","guides/ecommerce-automation-blueprint.html",
        "guides/cashflow-marketplace-seller.html","guides/ai-marketplace-listing.html",
        "guides/cross-platform-profit-comparison.html",
        "amazon-seller-profit-calculator.html","etsy-seller-profit-calculator.html",
        "ebay-seller-profit-calculator.html","shopify-seller-profit-calculator.html",
    ]
    xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in dict.fromkeys(urls): xml.append(f"<url><loc>https://dana-909.github.io/earnagent/store/{u}</loc></url>")
    xml.append("</urlset>")
    (ROOT/"sitemap.xml").write_text("\n".join(xml),encoding="utf-8")

def main():
    products=[]
    for p in choose_catalog_plan():
        path=write_product(p)
        q=dict(p); q["file"]=str(path); q["sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
        products.append(q)
    lemon_state=lemon_commercial_state()
    render_store(products,lemon_state)
    render_direct_checkout(products)
    render_discovery_files(products)
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),
             "products_generated":len(products),
             "catalog_value_usd":round(sum(p["price"] for p in products),2),
             "wallet":WALLET,"payment_network":"Base","payment_asset":"USDC",
             "lemon_squeezy":lemon_state,"products":products,
             "real_sales":lemon_state.get("live_paid_orders",0),
             "verified_revenue_usd":lemon_state.get("verified_revenue_usd",0),
             "rule":"Never count views, listings or simulated orders as revenue; only verified payment/order events count."}
    STATE.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(json.dumps(payload,ensure_ascii=False))

if __name__=="__main__":
    main()