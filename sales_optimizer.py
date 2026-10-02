import json
from pathlib import Path
from datetime import datetime, timezone

STATE=Path("data/sales_experiments.json")
STATE.parent.mkdir(exist_ok=True)
NICHES=[
("local-service-admin","Local Service Admin Kit"),("creator-sponsorship","Creator Sponsorship Kit"),
("real-estate","Real Estate Lead Tracker"),("restaurant-ops","Small Restaurant Ops Kit"),
("construction","Small Contractor Job Kit"),("online-course","Course Creator Launch Kit"),
("freelance-design","Designer Client Kit"),("job-search","Job Search Command Center"),
("pet-services","Pet Service Client Kit"),("beauty-services","Beauty Service Business Kit"),
("photography","Photography Client Kit"),("ecommerce","Small E-commerce Ops Kit")]
def main():
    try: s=json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception: s={}
    s["cycles"]=int(s.get("cycles",0))+1
    ex=s.get("experiments",[]); seen={x["slug"] for x in ex}
    added=[]
    for slug,title in NICHES:
        if slug not in seen and len(added)<3:
            ex.append({"slug":slug,"title":title,"created_at":datetime.now(timezone.utc).isoformat(),"views":0,"verified_sales":0,"verified_revenue_usd":0.0,"status":"test"})
            added.append(slug)
    for x in ex:
        x["score"]=round(float(x.get("verified_revenue_usd",0))*100 + float(x.get("verified_sales",0))*10,4)
    ex.sort(key=lambda x:x["score"],reverse=True)
    s["experiments"]=ex
    s["top_experiments"]=ex[:10]
    s["lesson"]="No verified sales yet; keep testing new niches." if not ex or ex[0]["verified_revenue_usd"]<=0 else "Scale only niches with verified revenue."
    STATE.write_text(json.dumps(s,ensure_ascii=False,separators=(",",":")))
    print(json.dumps({"cycle":s["cycles"],"new_niches":added,"experiments":len(ex),"lesson":s["lesson"]},ensure_ascii=False))
if __name__=="__main__": main()
