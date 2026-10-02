import json, os
from pathlib import Path
WALLET=os.getenv("TASKMARKET_WALLET_ADDRESS") or "0x948B78F80ba73E846B27171f31E3609b0e399701"
NETWORKS=[("base","Base",8453),("arbitrum","Arbitrum One",42161),("polygon","Polygon PoS",137),("optimism","Optimism",10)]
p=Path("store/index.html"); catalog=Path("data/sales_engine.json")
if p.exists() and catalog.exists():
 s=p.read_text(encoding="utf-8"); data=json.loads(catalog.read_text(encoding="utf-8"))
 blocks=[]
 for x in data.get("products",[]):
  links="".join(f'<a href="pay.html?product={x["slug"]}&network={k}">{n} — {float(x["price"]):.2f} USDC</a> ' for k,n,_ in NETWORKS)
  blocks.append(f'<div class="checkout"><b>{x["title"]}</b><p>{links}</p></div>')
 panel='<section class="pay"><h2>Direct USDC checkout</h2><p>Choose the network and product. Payment is verified on-chain.</p>'+''.join(blocks)+'</section>'
 start=s.find('<section class="pay">')
 if start>=0:
  end=s.find('</section>',start)
  if end>=0: s=s[:start]+s[end+10:]
 s=s.replace("</main>",panel+"</main>").replace("</style>"," .checkout{padding:12px;margin:10px 0;background:#24333d;border-radius:10px}.checkout a{display:inline-block;margin:4px 6px 4px 0;padding:8px;background:#18252e;border-radius:7px;text-decoration:none}</style>")
 p.write_text(s,encoding="utf-8")
print(json.dumps({"status":"ok","wallet":WALLET,"products":len(data.get("products",[])) if catalog.exists() else 0,"networks":[x[1] for x in NETWORKS]}))
