import json, os, re, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path("content"); ROOT.mkdir(exist_ok=True)
UA_RSS="https://trends.google.com/trending/rss?geo=UA"
WORLD_RSS="https://trends.google.com/trending/rss?geo=US"
FEEDS=[
 ("UA",UA_RSS),("WORLD",WORLD_RSS),
 ("NEWS","https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"),
]
FORMATS=[
 ("WHY_NOW","Why is everyone suddenly talking about {topic}?"),
 ("3_FACTS","3 things you probably don't know about {topic}"),
 ("HOT_TAKE","Max Vector explains {topic} in 30 seconds"),
 ("WOULD_YOU","Would you do this? The strange story behind {topic}"),
 ("COMMENT_BAIT","The internet is split about {topic}. Which side are you on?"),
 ("EXPLAINER","{topic} explained before you scroll"),
]
def fetch(url):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"EarnAgentTrendScout/1.0"})
        with urllib.request.urlopen(req,timeout=12) as r: return r.read().decode("utf-8","ignore")
    except Exception as e: return ""
def items(xml,limit=20):
    out=[]
    for m in re.findall(r"<item>(.*?)</item>",xml,re.S|re.I):
        title=re.search(r"<title>(.*?)</title>",m,re.S|re.I)
        if title:
            t=re.sub(r"<!\[CDATA\[|\]\]>","",title.group(1))
            t=re.sub(r"<[^>]+>","",t).strip()
            if t and t not in out: out.append(t)
        if len(out)>=limit: break
    return out
def clean(t): return re.sub(r"\s+"," ",t).strip()
def build():
    trends=[]
    for region,url in FEEDS:
        for t in items(fetch(url),18):
            trends.append({"region":region,"topic":clean(t)})
    # deduplicate and discard generic feed noise
    seen=set(); uniq=[]
    for x in trends:
        k=x["topic"].lower()
        if k not in seen and len(k)>5:
            seen.add(k); uniq.append(x)
    uniq=uniq[:30]
    # Own-trend experiments: formats that can become recognizable recurring memes/series.
    own=[
      {"region":"OWN","topic":"AI tries to solve an impossible everyday problem"},
      {"region":"OWN","topic":"One-minute internet courtroom: comment decides who is right"},
      {"region":"OWN","topic":"Human vs AI prediction: viewers vote before the reveal"},
      {"region":"OWN","topic":"The 10-second curiosity test: can you guess before the answer?"},
      {"region":"OWN","topic":"Max Vector investigates a suspiciously useful life hack"},
    ]
    queue=[]
    for x in uniq[:18]:
        for name,template in FORMATS[:3]:
            queue.append({"region":x["region"],"topic":x["topic"],"format":name,"hook":template.format(topic=x["topic"])})
    queue += [{"region":x["region"],"topic":x["topic"],"format":"ORIGINAL","hook":"You have 10 seconds. Can you solve this before Max Vector?"} for x in own]
    data={"generated_at":datetime.now(timezone.utc).isoformat(),"sources":FEEDS,"trends":uniq,"own_trend_tests":own,"queue":queue[:40]}
    (ROOT/"trend_radar.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    # Build publish-ready short scripts. No fake claims about trend volume.
    out=[]
    for i,q in enumerate(data["queue"][:20],1):
        topic=q["topic"]
        script=f"""HOOK: {q["hook"]}
CUT 1 (0-3s): Stop scrolling — {topic}.
CUT 2 (3-10s): Here is the one detail most people miss.
CUT 3 (10-22s): Give the useful/interesting explanation in plain language.
CUT 4 (22-28s): Ask the viewer to choose, predict, or disagree in comments.
CUT 5 (28-32s): Max Vector: “I’ll test the best comment next.”
CAPTION: {q["hook"]}
DISCLOSURE: Max Vector is a virtual AI-created presenter. Trend source: public feed snapshot; verify facts before publication.
"""
        out.append({"id":i,"format":q["format"],"region":q["region"],"topic":topic,"script":script})
    (ROOT/"shorts_queue.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":"ok","fresh_topics":len(uniq),"shorts_ready":len(out),"own_trend_tests":len(own)}))
if __name__=="__main__": build()
