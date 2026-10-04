import html
from pathlib import Path

ROOT=Path("store"); FREE=ROOT/"free"; NICHES=ROOT/"niches"; GUIDES=ROOT/"guides"
for p in (FREE,NICHES,GUIDES): p.mkdir(parents=True,exist_ok=True)

TOOLS=[
 ("marketplace-profit-checker","Free Marketplace Profit Leak Checker","Estimate margin leakage from fees, ads, returns, discounts and manual work.","marketplace-profit-leak-audit","$29"),
 ("seller-kpi-checker","Free Seller KPI Checker","Get a quick contribution-margin and AOV snapshot from a few marketplace numbers.","ecommerce-kpi-review-kit","$24"),
 ("cashflow-checker","Free Seller Cashflow Checker","Estimate your next payout cycle and the cash buffer left after planned outflows.","seller-cashflow-planner","$19"),
 ("cross-platform-profit-checker","Free Cross-Platform Profit Checker","Compare contribution across channels before choosing where to sell.","marketplace-profit-leak-audit","$29"),
]

GUIDE_ROWS=[
 ("marketplace-profit-leak-audit","Marketplace Profit Leak Audit for Sellers","Find the operational leaks that quietly reduce marketplace profit.","marketplace-profit-checker.html","marketplace-profit-leak-audit"),
 ("seller-margin-calculator","Marketplace Seller Margin Calculator","Estimate contribution margin after marketplace fees, advertising, returns and discounts.","marketplace-profit-checker.html","marketplace-profit-leak-audit"),
 ("seller-ops-dashboard","Marketplace Operations Dashboard","Track the metrics that matter weekly instead of juggling multiple spreadsheets.","seller-kpi-checker.html","marketplace-ops-dashboard"),
 ("ecommerce-automation-blueprint","Ecommerce Automation Blueprint","Map repetitive seller operations to practical AI and workflow automations.","seller-kpi-checker.html","marketplace-automation-blueprint"),
 ("cashflow-marketplace-seller","Marketplace Seller Cashflow Planner","Plan payouts, fees, advertising and upcoming cash needs in one lightweight workflow.","cashflow-checker.html","seller-cashflow-planner"),
 ("ai-marketplace-listing","AI Marketplace Listing Optimization","Build repeatable listing experiments instead of rewriting product copy blindly.","marketplace-profit-checker.html","ai-listing-optimization-kit"),
 ("cross-platform-profit-comparison","Cross-Platform Marketplace Profit Comparison","Compare contribution before choosing a marketplace.","cross-platform-profit-checker.html","marketplace-profit-leak-audit"),
]

def page(title,desc,product,price,body):
 return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — EarnAgent</title><meta name="description" content="{html.escape(desc)}"><style>body{{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}}main{{max-width:900px;margin:32px auto;padding:30px;background:#fff;border-radius:18px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}label{{display:block}}input,button{{font:inherit;padding:11px;margin:5px 0;box-sizing:border-box}}input{{width:100%}}button{{cursor:pointer}}.result{{font-size:1.15rem;font-weight:700}}.cta{{margin-top:24px;padding:18px;background:#eef5f8;border-radius:12px}}.buy{{display:inline-block;padding:12px 16px;background:#10202b;color:#fff;border-radius:9px;text-decoration:none}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><main><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p>{body}<div class="cta"><b>Found a problem worth fixing?</b><p>{html.escape(product)} — {html.escape(price)}</p><a class="buy" href="../pay.html?product={html.escape(product)}">Open secure USDC checkout</a><p><small>Payment is verified on-chain before a sale is counted.</small></p></div></main></body></html>"""

# Free acquisition tools.
(FREE/"marketplace-profit-checker.html").write_text(page("Free Marketplace Profit Leak Checker",TOOLS[0][2],TOOLS[0][3],TOOLS[0][4],"""<div class="grid"><label>Revenue ($)<input id="rev" type="number" value="5000"></label><label>Marketplace fees ($)<input id="fees" type="number" value="750"></label><label>Ads ($)<input id="ads" type="number" value="500"></label><label>Returns ($)<input id="ret" type="number" value="200"></label><label>Discounts ($)<input id="disc" type="number" value="100"></label><label>Manual hours<input id="mh" type="number" value="20"></label><label>Value/hour ($)<input id="hv" type="number" value="25"></label></div><button onclick="calc()">Check profit leaks</button><p id="out" class="result"></p><script>function calc(){let rev=+document.getElementById('rev').value,fees=+document.getElementById('fees').value,ads=+document.getElementById('ads').value,ret=+document.getElementById('ret').value,disc=+document.getElementById('disc').value,mh=+document.getElementById('mh').value,hv=+document.getElementById('hv').value;let leaks=fees+ads+ret+disc+mh*hv;let net=rev-leaks;document.getElementById('out').textContent='Listed leaks: $'+leaks.toFixed(2)+' · estimated contribution after them: $'+net.toFixed(2)+' ('+(rev?100*net/rev:0).toFixed(1)+'%)'}</script>"""),encoding="utf-8")
(FREE/"seller-kpi-checker.html").write_text(page("Free Seller KPI Checker",TOOLS[1][2],TOOLS[1][3],TOOLS[1][4],"""<div class="grid"><label>Orders<input id="orders" type="number" value="100"></label><label>Revenue ($)<input id="rev" type="number" value="5000"></label><label>Fees ($)<input id="fees" type="number" value="750"></label><label>Ads ($)<input id="ads" type="number" value="500"></label></div><button onclick="calc()">Check seller KPIs</button><p id="out" class="result"></p><script>function calc(){let o=+orders.value,rev=+document.getElementById('rev').value,fees=+document.getElementById('fees').value,ads=+document.getElementById('ads').value;let aov=o?rev/o:0,m=rev?100*(rev-fees-ads)/rev:0;out.textContent='AOV: $'+aov.toFixed(2)+' · contribution after fees + ads: '+m.toFixed(1)+'%'}</script>"""),encoding="utf-8")
(FREE/"cashflow-checker.html").write_text(page("Free Seller Cashflow Checker",TOOLS[2][2],TOOLS[2][3],TOOLS[2][4],"""<div class="grid"><label>Next payout ($)<input id="p" type="number" value="5000"></label><label>Fees due ($)<input id="f" type="number" value="750"></label><label>Ads planned ($)<input id="a" type="number" value="500"></label><label>Other outflows ($)<input id="o" type="number" value="800"></label><label>Cash on hand ($)<input id="c" type="number" value="3000"></label></div><button onclick="calc()">Calculate buffer</button><p id="out" class="result"></p><script>function calc(){let net=+p.value-+f.value-+a.value-+o.value;out.textContent='Net payout cycle: $'+net.toFixed(2)+' · estimated cash after cycle: $'+(+c.value+net).toFixed(2)}</script>"""),encoding="utf-8")
(FREE/"cross-platform-profit-checker.html").write_text(page("Free Cross-Platform Profit Checker",TOOLS[3][2],TOOLS[3][3],TOOLS[3][4],"""<div class="grid"><label>Selling price ($)<input id="price" type="number" value="50"></label><label>Product cost ($)<input id="cost" type="number" value="20"></label><label>Shipping ($)<input id="ship" type="number" value="5"></label><label>Ads ($)<input id="ads" type="number" value="5"></label></div><p>Platform fee rates:</p><div class="grid"><label>A %<input id="a" type="number" value="15"></label><label>B %<input id="b" type="number" value="12"></label><label>C %<input id="c" type="number" value="10"></label></div><button onclick="calc()">Compare</button><p id="out" class="result"></p><script>function calc(){let p=+price.value,base=p-+cost.value-+ship.value-+ads.value;let rows=[["A",+a.value],["B",+b.value],["C",+c.value]].map(x=>[x[0],base-p*x[1]/100]).sort((x,y)=>y[1]-x[1]);out.textContent=rows.map(x=>x[0]+": $"+x[1].toFixed(2)+" contribution").join(" · ")}</script>"""),encoding="utf-8")


for slug,title,desc,free,product in GUIDE_ROWS:
 body=f"""<div class="cta"><b>Start free:</b> <a href="../free/{html.escape(free)}">Open the free calculator</a></div><h2>Why this matters</h2><p>Marketplace sellers often have revenue but incomplete visibility into contribution margin, operational cost and repetitive work. This guide focuses on measurable inputs and a small number of actions.</p><ol><li>Run the free tool.</li><li>Identify the largest leak.</li><li>Fix one bottleneck.</li><li>Measure the next cycle.</li></ol>"""
 (GUIDES/(slug+".html")).write_text(page(title,desc,product,"see store",body),encoding="utf-8")

(NICHES/"marketplace-sellers.html").write_text(page("Marketplace Seller Profit & Automation Tools","Free calculators and reusable workflows for marketplace sellers who want better margins and less manual work.","Marketplace Automation Blueprint","$79","<p>Start with a free profit-leak check, then move to reusable operating tools when the workflow proves useful.</p><p><a href='../free/marketplace-profit-checker.html'>Free profit checker</a></p>"),encoding="utf-8")

(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://dana-909.github.io/earnagent/store/'+x+'</loc></url>' for x in ["","free/marketplace-profit-checker.html","free/seller-kpi-checker.html","free/cashflow-checker.html","free/cross-platform-profit-checker.html","niches/marketplace-sellers.html"])+''.join('<url><loc>https://dana-909.github.io/earnagent/store/guides/'+x[0]+'.html</loc></url>' for x in GUIDE_ROWS)+'</urlset>',encoding="utf-8")
(ROOT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: sitemap.xml\n",encoding="utf-8")
print({"free_tools":len(TOOLS),"guides":len(GUIDE_ROWS),"niches":1,"status":"built"})


# Platform-intent acquisition pages. These use generic seller-profit language rather than
# asserting current platform fee schedules, so they remain useful without brittle claims.
PLATFORM_PAGES = [
 ("amazon-seller-profit-calculator","Amazon Seller Profit Calculator","Estimate contribution margin for an Amazon-style marketplace workflow using your own fee, ad, return and fulfillment inputs.","marketplace-profit-checker.html","marketplace-profit-rescue-report"),
 ("etsy-seller-profit-calculator","Etsy Seller Profit Calculator","Estimate contribution after your own marketplace fees, ads, discounts, returns and operating time.","marketplace-profit-checker.html","marketplace-profit-rescue-report"),
 ("ebay-seller-profit-calculator","eBay Seller Profit Calculator","Compare seller contribution after the costs you actually incur on an eBay-style marketplace workflow.","marketplace-profit-checker.html","marketplace-profit-rescue-report"),
 ("shopify-seller-profit-calculator","Shopify Seller Profit Calculator","Model store contribution, advertising, refunds and operating time using your own numbers.","marketplace-profit-checker.html","marketplace-profit-rescue-report"),
]

for slug,title,desc,free,product in PLATFORM_PAGES:
 body=f"""<div class="cta"><b>Run the free model first:</b> <a href="../free/{html.escape(free)}">Open the profit checker</a></div>
 <h2>What this calculator measures</h2>
 <p>Enter your own selling price, product cost, transaction costs, advertising, refunds and operating time. The goal is to estimate contribution from your actual economics rather than assume a platform fee schedule.</p>
 <h2>Simple workflow</h2><ol><li>Enter one representative product or order.</li><li>Include every cost you actually pay.</li><li>Compare contribution before and after operational changes.</li><li>Repeat monthly as your economics change.</li></ol>"""
 (GUIDES/(slug+".html")).write_text(page(title,desc,product,"see store",body),encoding="utf-8")

# Rebuild sitemap after adding platform-intent pages.
urls = ["","free/marketplace-profit-checker.html","free/seller-kpi-checker.html","free/cashflow-checker.html","free/cross-platform-profit-checker.html","niches/marketplace-sellers.html","dealpilot/index.html","dealpilot/subscription-break-even.html","dealpilot/phone-total-cost.html","dealpilot/car-monthly-cost.html","dealpilot/buy-vs-rent.html","earnings.html"]
urls += ["guides/"+x[0]+".html" for x in GUIDE_ROWS]
urls += ["guides/"+x[0]+".html" for x in PLATFORM_PAGES]
(ROOT/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://dana-909.github.io/earnagent/store/'+x+'</loc></url>' for x in urls)+'</urlset>',encoding="utf-8")
