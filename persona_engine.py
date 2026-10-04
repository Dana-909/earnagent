import json, os
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path("content"); ROOT.mkdir(exist_ok=True)
PERSONA={
  "name":"Max Vector",
  "handle":"@maxvector.ai",
  "role":"AI business builder who tests ways to make useful digital work sellable",
  "promise":"No hype: build it, measure it, show the receipt.",
  "tone":"direct, practical, skeptical of easy-money claims",
  "audience":"people who want to use AI to build small digital income streams",
  "disclosure":"Virtual AI-created presenter. Examples and revenue claims are labeled as such."
}
LESSONS=[
 ("01","AI that actually does a job","Stop asking AI for ideas. Give it a customer, a deliverable and a price."),
 ("02","The 20-minute product test","Build one tiny outcome people can understand in one sentence."),
 ("03","Why most AI side hustles make $0","A catalog is not demand. Traffic is not revenue. Revenue needs a buyer and a payment rail."),
 ("04","Turn one skill into three products","Package the same capability as a checklist, a template and a done-for-you service."),
 ("05","Build before you brand","A useful result beats a beautiful logo when you have no customers."),
 ("06","How to price a digital product","Price around the value of the outcome, then test a low-friction entry product."),
 ("07","The honest AI income dashboard","Track visitors, leads, purchases and verified payouts separately."),
 ("08","Automate the boring part","Let software produce drafts, QA files and publish updates; keep identity and payment approvals human."),
]
def slug(s): return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")
def make():
    lessons=[]
    for n,title,hook in LESSONS:
        lessons.append({"episode":n,"title":title,"hook":hook,
          "short_script":f"HOOK: {hook}\n\nBODY: Max Vector tests one concrete workflow. The rule is simple: create a measurable outcome first, then put a real price next to it. Never call an impression, listing or simulated order revenue.\n\nCTA: Follow Max Vector for the next test. Full lesson: /content/course/episode-{n}.html",
          "video_title":f"{title} | Max Vector AI",
          "description":f"{hook} This episode is an experiment, not a promise of income. Virtual presenter: Max Vector. #AI #automation #digitalproducts"})
    (ROOT/"persona.json").write_text(json.dumps(PERSONA,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"content_calendar.json").write_text(json.dumps({"generated_at":datetime.now(timezone.utc).isoformat(),"episodes":lessons},ensure_ascii=False,indent=2),encoding="utf-8")
    c=ROOT/"course"; c.mkdir(exist_ok=True)
    for x in lessons:
        html=f'''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{x["title"]} — Max Vector</title><style>body{{font:18px system-ui;max-width:760px;margin:40px auto;padding:0 20px;line-height:1.6;background:#0b1020;color:#eef2ff}}h1{{font-size:42px}}.tag{{color:#67e8f9}}.box{{padding:22px;border:1px solid #334155;border-radius:16px;background:#111827}}a{{color:#67e8f9}}</style><body><p class="tag">MAX VECTOR · AI BUSINESS LAB</p><h1>{x["title"]}</h1><div class="box"><p><b>Hook:</b> {x["hook"]}</p><p>{x["short_script"].replace(chr(10),"<br>")}</p></div><p><small>{PERSONA["disclosure"]}</small></p><p><a href="../">Back to the lab</a></p></body></html>'''
        (c/f'episode-{x["episode"]}.html').write_text(html,encoding="utf-8")
    index=f'''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Max Vector AI Business Lab</title><style>body{{margin:0;font:18px system-ui;background:#080c16;color:#eef2ff}}main{{max-width:1050px;margin:auto;padding:55px 22px}}h1{{font-size:clamp(42px,8vw,78px);line-height:.95}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}article{{padding:22px;border:1px solid #263247;border-radius:18px;background:#101827}}a{{color:#67e8f9}}.avatar{{width:150px;height:150px;border-radius:50%;background:linear-gradient(145deg,#172554,#0891b2);display:grid;place-items:center;font-size:55px;font-weight:800}}small{{color:#94a3b8}}</style><main><div class="avatar">MV</div><p>MAX VECTOR · AI BUSINESS LAB</p><h1>Build it. Measure it. Show the receipt.</h1><p>{PERSONA["promise"]} No fake revenue, no fake screenshots.</p><div class="grid">{"".join(f'<article><h2>{x["title"]}</h2><p>{x["hook"]}</p><a href="course/episode-{x["episode"]}.html">Free lesson →</a></article>' for x in lessons)}</div><p><small>{PERSONA["disclosure"]}</small></p></main></html>'''
    (ROOT/"index.html").write_text(index,encoding="utf-8")
    # machine-readable feed for future publishing adapters
    feed={"title":"Max Vector AI Business Lab","handle":PERSONA["handle"],"episodes":[{"title":x["video_title"],"description":x["description"],"script":x["short_script"]} for x in lessons]}
    (ROOT/"publish_queue.json").write_text(json.dumps(feed,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"ok","persona":PERSONA["name"],"episodes":len(lessons),"course":"content/course","publish_queue":"content/publish_queue.json"}))
if __name__=="__main__": make()
