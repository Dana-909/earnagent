import json
from pathlib import Path
WALLET="0x948B78F80ba73E846B27171f31E3609b0e399701"
NETWORKS=[("Base",8453,"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),("Arbitrum One",42161,"0xaf88d065e77c8cC2239327C5EDb3A432268e5831"),("Polygon PoS",137,"0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"),("Optimism",10,"0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85")]
p=Path("store/index.html")
if p.exists():
 s=p.read_text(encoding="utf-8")
 rows=[]
 for name,chain,usdc in NETWORKS:
  rows.append(f"<li><a href=\"ethereum:{usdc}@{chain}/transfer?address={WALLET}\">Pay with {name} USDC</a></li>")
 panel="<section class=\"pay\"><h2>Direct USDC payment</h2><p>No account required. Choose a network:</p><ul>"+"" .join(rows)+"</ul><p>Wallet: <code>"+WALLET+"</code></p><small>Only native USDC payments verified on-chain are counted.</small></section>"
 if "Direct USDC payment" not in s: p.write_text(s.replace("</main>",panel+"</main>"),encoding="utf-8")
print(json.dumps({"status":"ok","networks":[x[0] for x in NETWORKS]}))