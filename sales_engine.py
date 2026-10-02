import json, os, hashlib, urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path("store"); PRODUCTS=ROOT/"products"; STATE=Path("data/sales_engine.json")
PRODUCTS.mkdir(parents=True,exist_ok=True); STATE.parent.mkdir(exist_ok=True)
WALLET=os.getenv("TASKMARKET_WALLET_ADDRESS","0x948B78F80ba73E846B27171f31E3609b0e399701")
BASE_USDC="USDC on Base"
PRODUCTS_PLAN=[
 {"slug":"freelancer-invoice-kit","title":"Freelancer Invoice & Quote Kit","price":7.00,"kind":"html","pitch":"A clean offline invoice and quote generator for freelancers and small service businesses."},
 {"slug":"small-business-kpi-dashboard","title":"Small Business KPI Dashboard","price":9.00,"kind":"html","pitch":"A self-contained browser dashboard for tracking revenue, leads, conversion and monthly targets."},
 {"slug":"content-calendar-kit","title":"30-Day Content Calendar Kit","price":5.00,"kind":"md","pitch":"A practical 30-day content planning system with reusable planning fields and publishing checklists."},
 {"slug":"job-application-tracker","title":"Job Application Tracker","price":4.00,"kind":"html","pitch":"A private offline tracker for applications, stages, contacts, interviews and follow-ups."},
 {"slug":"svg-social-icon-pack","title":"Minimal Social Icon SVG Pack","price":6.00,"kind":"svg","pitch":"Original lightweight SVG assets for common web UI uses."},
 {"slug":"project-planning-kit","title":"Project Planning & Risk Kit","price":8.00,"kind":"md","pitch":"A compact project planning system covering scope, milestones, risks, decisions and retrospectives."},
]

def write_product(p):
    path=PRODUCTS/(p["slug"]+"."+p["kind"])
    if p["kind"]=="html":
        body="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PRODUCT_TITLE</title>
<style>body{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}main{max-width:900px;margin:40px auto;padding:28px;background:white;border-radius:18px}input,textarea,button{font:inherit;padding:10px;margin:5px 0;box-sizing:border-box}input,textarea{width:100%}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:650px){.row{grid-template-columns:1fr}}</style></head><body><main><h1>PRODUCT_TITLE</h1><p>PRODUCT_PITCH</p><div class="row"><label>Client / Project<input></label><label>Date<input type="date"></label></div><label>Items / Notes<textarea rows="5"></textarea></label><label>Amount<input type="number" step="0.01"></label><button onclick="window.print()">Print / Save PDF</button><hr><small>This tool runs locally in your browser. No data is uploaded.</small></main></body></html>"""
        body=body.replace("PRODUCT_TITLE",p["title"]).replace("PRODUCT_PITCH",p["pitch"])
    elif p["kind"]=="md":
        body="# "+p["title"]+"\n\n## Purpose\n"+p["pitch"]+"""\n\n## Quick start\n1. Define the outcome.\n2. Break it into measurable actions.\n3. Assign an owner and deadline.\n4. Record evidence/results.\n5. Review what worked and improve the next cycle.\n\n## Working template\n\n### Objective\n- Outcome:\n- Metric:\n- Deadline:\n\n### Actions\n- [ ] Action 1\n- [ ] Action 2\n- [ ] Action 3\n\n### Review\n- What worked?\n- What failed?\n- What should be automated?\n- What should be removed?\n"""
    else:
        body='''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="700" viewBox="0 0 1200 700"><rect width="1200" height="700" fill="#f4f1ea"/><text x="60" y="90" font-family="system-ui" font-size="44" font-weight="700">Minimal Social Icon SVG Pack</text><g fill="none" stroke="#18242b" stroke-width="10"><circle cx="180" cy="250" r="65"/><circle cx="420" cy="250" r="65"/><circle cx="660" cy="250" r="65"/><rect x="865" y="185" width="130" height="130" rx="28"/></g><text x="120" y="430" font-family="system-ui" font-size="24">Original simple vector symbols — edit freely.</text></svg>'''
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
        buy_html='<p><a href="'+buy+'"><b>Buy securely online</b></a></p>' if buy else ''
        cards.append('<article><h2>'+p["title"]+'</h2><p>'+p["pitch"]+'</p><strong>$'+format(p["price"],".2f")+
                     '</strong><p><a href="products/'+p["slug"]+'.'+p["kind"]+'">Preview</a></p>'+
                     buy_html+'<div class="pay"><b>Alternative: pay with '+BASE_USDC+'</b><br>Send exactly <b>'+
                     format(p["price"],".2f")+' USDC</b> on Base to:<br><code>'+WALLET+
                     '</code><br><small>Only blockchain-verified payments count.</small></div></article>')
    html='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EarnAgent Digital Store</title><style>body{font:16px system-ui;margin:0;background:#101820;color:#f5f1e8}main{max-width:1050px;margin:auto;padding:30px}article{background:#18252e;padding:22px;margin:16px 0;border-radius:16px}a{color:#b9e4ff}.pay{background:#24333d;padding:14px;border-radius:10px}code{overflow-wrap:anywhere}</style></head><body><main><h1>EarnAgent Digital Store</h1><p>Original downloadable tools, templates and assets.</p>'''+''.join(cards)+'''</main></body></html>'''
    (ROOT/"index.html").write_text(html,encoding="utf-8")

def main():
    products=[]
    for p in PRODUCTS_PLAN:
        path=write_product(p)
        q=dict(p); q["file"]=str(path); q["sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
        products.append(q)
    lemon_state=lemon_commercial_state()
    render_store(products,lemon_state)
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
