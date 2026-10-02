"""Persistent learning memory for the autonomous office."""
import json
from pathlib import Path

PATH = Path("data/office_memory.json")
MAX = 200

def load():
    try:
        data=json.loads(PATH.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {"cases":[]}
    except Exception:
        return {"cases":[]}

def remember(task, fmt, office_result, outcome=None):
    data=load()
    cases=data.setdefault("cases",[])
    item={
        "task_id":str(task.get("task_id") or ""),
        "mode":task.get("mode"),
        "format":fmt,
        "reward_usd":float(task.get("reward_usd") or 0),
        "decision":office_result.get("decision"),
        "audit":office_result.get("office_context",{}).get("audit"),
        "outcome":outcome or "unknown",
    }
    cases.append(item)
    data["cases"]=cases[-MAX:]
    PATH.parent.mkdir(parents=True,exist_ok=True)
    PATH.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf-8")

def context(task, fmt, limit=8):
    data=load()
    cases=data.get("cases",[])
    same=[x for x in cases if x.get("format")==fmt]
    return same[-limit:]
