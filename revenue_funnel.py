import html
from pathlib import Path

ROOT=Path("store")
FREE=ROOT/"free"
FREE.mkdir(parents=True,exist_ok=True)

TOOLS=[
 ("invoice-estimator","Free Invoice & Quote Estimator","Estimate invoice totals and create a print-ready quote in your browser.","freelancer-invoice-kit","$7"),
 ("kpi-checker","Free Small-Business KPI Checker","Enter four numbers and instantly see conversion and revenue-per-lead metrics.","small-business-kpi-dashboard","$9"),
 ("job-tracker-lite","Free Job Application Tracker","A lightweight private tracker you can use before upgrading to the full application kit.","job-application-tracker","$4"),
]



ACQUISITION_GUIDES=[
 ("invoice-template-freelancer","Invoice Template for Freelancers","A practical browser-first workflow for creating quotes and estimating invoice totals. Start free, then use the reusable invoice kit.","invoice-estimator.html","freelancer-invoice-kit"),
 ("invoice-quote-small-business","Invoice and Quote Workflow for Small Businesses","Estimate project totals quickly and keep a repeatable quote workflow instead of rebuilding documents from scratch.","invoice-estimator.html","freelancer-invoice-kit"),
 ("kpi-calculator-small-business","Small Business KPI Calculator","Calculate conversion rate, revenue per lead and ROAS from four simple inputs.","kpi-checker.html","small-business-kpi-dashboard"),
 ("lead-conversion-calculator","Lead Conversion Calculator","Turn lead and customer counts into a quick conversion benchmark you can use for weekly reviews.","kpi-checker.html","small-business-kpi-dashboard"),
 ("job-application-tracker-free","Free Job Application Tracker","Track company, role, stage and follow-up notes privately in your browser.","job-tracker-lite.html","job-application-tracker"),
 ("interview-follow-up-tracker","Interview Follow-Up Tracker","Keep interview follow-ups organized and reduce the chance of losing track of the next action.","job-tracker-lite.html","job-application-tracker"),
 ("creator-content-planner","Creator Content Planner","Use a simple planning workflow to turn a blank month into a repeatable publishing calendar.","invoice-estimator.html","content-calendar-kit"),
 ("freelancer-client-workflow","Freelancer Client Workflow","A lightweight workflow for keeping project notes, amounts and deliverables organized.","invoice-estimator.html","freelancer-invoice-kit"),
 ("contractor-project-risk","Contractor Project Risk Checklist","A compact workflow for scope, milestones and project risks before work gets expensive.","kpi-checker.html","project-planning-kit"),
 ("small-team-project-planner","Small Team Project Planner","Organize objectives, actions, owners and review notes without a heavyweight project system.","kpi-checker.html","project-planning-kit"),
 ("designer-social-assets","Minimal Social Icons for Designers","Preview a lightweight original SVG asset pack for common interface work.","job-tracker-lite.html","svg-social-icon-pack"),
 ("business-dashboard-template","Small Business Dashboard Template","Start with a simple KPI workflow and upgrade to a reusable dashboard kit when needed.","kpi-checker.html","small-business-kpi-dashboard"),
]

def build_acquisition_guides():
    n=ROOT/"guides"; n.mkdir(parents=True,exist_ok=True)
    for slug,title,desc,free_slug,product_slug in ACQUISITION_GUIDES:
        body=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — EarnAgent</title><meta name="description" content="{html.escape(desc)}">
<style>body{{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}}main{{max-width:860px;margin:30px auto;padding:30px;background:#fff;border-radius:18px}}.box{{background:#eef5f8;padding:20px;border-radius:14px}}a.cta{{display:inline-block;padding:11px 15px;background:#18242b;color:#fff;text-decoration:none;border-radius:9px;margin-right:8px}}</style></head><body><main>
<h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p><div class="box"><h2>Start with the free tool</h2><p>Try the browser tool first. No account is required for the basic workflow.</p><a class="cta" href="../free/{html.escape(free_slug)}">Open free tool</a><a class="cta" href="../index.html">View paid kits</a></div>
<h2>Why this workflow?</h2><p>The goal is to reduce repetitive setup and make a useful result available quickly. If the free workflow is useful, the related paid kit adds a reusable version for repeated work.</p>
<h2>Simple workflow</h2><ol><li>Open the free tool.</li><li>Use it on one real task.</li><li>Keep the result if it saves time.</li><li>Upgrade only if you need the reusable kit.</li></ol>
<p><small>EarnAgent digital products are independent tools and templates. Results depend on your own use and circumstances.</small></p></main></body></html>"""
        (n/(slug+".html")).write_text(body,encoding="utf-8")
    links="".join("<li><a href='"+x[0]+".html'>"+html.escape(x[1])+"</a></li>" for x in ACQUISITION_GUIDES)
    (n/"index.html").write_text("<!doctype html><meta charset='utf-8'><title>EarnAgent practical guides</title><h1>Practical guides and free tools</h1><ul>"+links+"</ul>",encoding="utf-8")

NICHE_PAGES=[
 ("freelancer-invoice","Free Invoice Template for Freelancers","Create a clean quote and invoice workflow in minutes. Use the free estimator, then upgrade to the reusable Freelancer Invoice & Quote Kit.","invoice-estimator.html","freelancer-invoice-kit","Freelancer Invoice & Quote Kit","$7"),
 ("small-business-kpi","Small Business KPI Dashboard","Track leads, conversion, revenue per lead and marketing efficiency with a simple browser workflow.","kpi-checker.html","small-business-kpi-dashboard","Small Business KPI Dashboard","$9"),
 ("job-search-tracker","Job Application Tracker","Keep applications, interviews and follow-ups organized privately in your browser.","job-tracker-lite.html","job-application-tracker","Job Application Tracker","$4"),
 ("creator-content-calendar","30-Day Content Calendar for Creators","Plan a month of publishing with a practical content workflow instead of starting from a blank page.","invoice-estimator.html","content-calendar-kit","30-Day Content Calendar Kit","$5"),
 ("contractor-project-planning","Project Planning Kit for Small Contractors","Organize scope, milestones, risks and decisions in one compact planning system.","kpi-checker.html","project-planning-kit","Project Planning & Risk Kit","$8"),
 ("designer-client-workflow","Client Workflow Kit for Freelance Designers","Keep client work, decisions and project handoffs organized with reusable lightweight templates.","job-tracker-lite.html","svg-social-icon-pack","Minimal Social Icon SVG Pack","$6"),
]

def niche_page(slug,title,desc,free_slug,product_slug,product_title,price):
    body=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — EarnAgent</title><meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">
<style>body{{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}}main{{max-width:900px;margin:32px auto;padding:30px;background:#fff;border-radius:18px}}.hero{{padding:22px;background:#eef5f8;border-radius:14px}}.cta{{display:inline-block;padding:12px 16px;background:#18242b;color:#fff;text-decoration:none;border-radius:10px;margin:8px 8px 8px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0}}.grid div{{padding:16px;background:#f7f7f5;border-radius:12px}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><main>
<div class="hero"><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p><a class="cta" href="../free/{html.escape(free_slug)}">Try the free tool</a><a class="cta" href="../index.html">See the full store</a></div>
<div class="grid"><div><b>Fast</b><br>Runs in the browser.</div><div><b>Private</b><br>Designed for lightweight local workflows.</div><div><b>Reusable</b><br>Upgrade when the free tool is not enough.</div></div>
<h2>Free first, paid when useful</h2><p>Use the free tool without an account. If it solves the immediate problem and you need a reusable kit, the paid product is <b>{html.escape(product_title)}</b> for {html.escape(price)}.</p>
<p><a class="cta" href="../index.html">View {html.escape(product_title)}</a></p>
<p><small>EarnAgent products are independent digital tools and templates. No guarantee of business, job, or financial results.</small></p>
</main></body></html>"""
    (ROOT/"niches"/(slug+".html")).write_text(body,encoding="utf-8")

def build_niche_pages():
    n=ROOT/"niches"; n.mkdir(parents=True,exist_ok=True)
    for row in NICHE_PAGES: niche_page(*row)
    links="".join("<li><a href='"+s+".html'>"+html.escape(t)+"</a> — "+html.escape(d)+"</li>" for s,t,d,*_ in NICHE_PAGES)
    (n/"index.html").write_text("<!doctype html><meta charset='utf-8'><title>EarnAgent guides and tools</title><h1>EarnAgent guides and tools</h1><p>Free browser tools and reusable digital kits for practical work.</p><ul>"+links+"</ul>",encoding="utf-8")

def page(slug,title,desc,product,price,body):
    c=f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — EarnAgent</title><meta name="description" content="{html.escape(desc)}">
<style>body{{font:16px system-ui;margin:0;background:#f4f1ea;color:#18242b}}main{{max-width:850px;margin:35px auto;padding:28px;background:#fff;border-radius:18px}}input,button,textarea{{font:inherit;padding:11px;margin:5px 0;box-sizing:border-box}}input{{width:100%}}button{{cursor:pointer}}.cta{{margin-top:24px;padding:18px;background:#eef5f8;border-radius:12px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}}}.result{{font-size:1.15rem;font-weight:700}}</style></head><body><main>
<h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p>{body}
<div class="cta"><b>Need the full reusable version?</b><p>{html.escape(product)} — {price}</p><a href="../index.html">View the EarnAgent store</a></div>
</main></body></html>"""
    (FREE/slug).write_text(c,encoding="utf-8")

page("invoice-estimator.html",TOOLS[0][1],TOOLS[0][2],TOOLS[0][3],TOOLS[0][4],"""<div class="grid"><label>Hours<input id="h" type="number" value="10" min="0"></label><label>Hourly rate ($)<input id="r" type="number" value="50" min="0"></label><label>Expenses ($)<input id="e" type="number" value="0" min="0"></label><label>Tax (%)<input id="t" type="number" value="0" min="0"></label></div><button onclick="calc()">Calculate</button><p id="out" class="result"></p><script>function calc(){let h=+document.getElementById('h').value,r=+document.getElementById('r').value,e=+document.getElementById('e').value,t=+document.getElementById('t').value;let sub=h*r+e,total=sub*(1+t/100);document.getElementById('out').textContent='Estimated total: $'+total.toFixed(2)}</script>""")

page("kpi-checker.html",TOOLS[1][1],TOOLS[1][2],TOOLS[1][3],TOOLS[1][4],"""<div class="grid"><label>Leads<input id="l" type="number" value="100" min="0"></label><label>Customers<input id="c" type="number" value="10" min="0"></label><label>Revenue ($)<input id="rev" type="number" value="1000" min="0"></label><label>Marketing spend ($)<input id="sp" type="number" value="200" min="0"></label></div><button onclick="calc()">Check KPIs</button><p id="out" class="result"></p><script>function calc(){let l=+document.getElementById('l').value,c=+document.getElementById('c').value,rev=+document.getElementById('rev').value,sp=+document.getElementById('sp').value;let cr=l?100*c/l:0, rpl=l?rev/l:0,roas=sp?rev/sp:0;document.getElementById('out').textContent='Conversion '+cr.toFixed(1)+'% · Revenue/lead $'+rpl.toFixed(2)+' · ROAS '+roas.toFixed(2)+'x'}</script>""")

page("job-tracker-lite.html",TOOLS[2][1],TOOLS[2][2],TOOLS[2][3],TOOLS[2][4],"""<label>Company<input id="co" placeholder="Company name"></label><label>Role<input id="role" placeholder="Role"></label><label>Status<textarea id="st" rows="3" placeholder="Applied / Interview / Follow-up"></textarea></label><button onclick="save()">Save locally</button><p id="out" class="result"></p><script>function save(){let x={company:co.value,role:role.value,status:st.value};localStorage.setItem('earnagent-job',JSON.stringify(x));out.textContent='Saved only in this browser.'}</script>""")

links=["<li><a href='free/"+s+".html'>"+html.escape(t)+"</a> — "+html.escape(d)+"</li>" for s,t,d,_,_ in TOOLS]
index=ROOT/"index.html"
if index.exists():
    old=index.read_text(encoding="utf-8")
    marker="<!-- EARNAGENT_FREE_TOOLS -->"
    block=marker+"<section><h2>Free tools</h2><p>Try these instantly, then upgrade if you need the full reusable kit.</p><ul>"+''.join(links)+"</ul></section>"
    if marker in old:
        old=old.split(marker)[0]+block+old.split(marker,1)[1].split("</section>",1)[-1] if "</section>" in old.split(marker,1)[1] else old
    else:
        old=old.replace("</main>",block+"</main>")
    niche_links="<section><h2>Work-specific guides</h2><p>Free tools and focused workflows for common jobs.</p><ul>"+''.join("<li><a href='niches/"+x[0]+".html'>"+html.escape(x[1])+"</a></li>" for x in NICHE_PAGES)+"</ul></section>"
    if "</main>" in old:
        old=old.replace("</main>",niche_links+"</main>")
    index.write_text(old,encoding="utf-8")

(FREE/"index.html").write_text("<!doctype html><meta charset='utf-8'><title>Free EarnAgent tools</title><h1>Free EarnAgent tools</h1><ul>"+''.join(links)+"</ul>",encoding="utf-8")
build_niche_pages()
build_acquisition_guides()
# Publish a fresh crawl map after all generated acquisition pages exist.
base_urls=["store/","store/free/","store/niches/"]+[("store/free/"+x[0]+".html") for x in TOOLS]+[("store/niches/"+x[0]+".html") for x in NICHE_PAGES]+["store/guides/"]+[("store/guides/"+x[0]+".html") for x in ACQUISITION_GUIDES]
xml="<?xml version=\"1.0\" encoding=\"UTF-8\"?><urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"+"".join("<url><loc>"+html.escape(u)+"</loc></url>" for u in base_urls)+"</urlset>"
(ROOT/"sitemap.xml").write_text(xml,encoding="utf-8")
(ROOT/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: sitemap.xml\n",encoding="utf-8")
print({"free_tools_and_niche_pages":len(TOOLS),"niche_pages":len(NICHE_PAGES),"acquisition_guides":len(ACQUISITION_GUIDES),"status":"built"})
