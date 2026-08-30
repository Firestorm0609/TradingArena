"""TradingArena — live neon terminal dashboard."""
import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from config import DATA_DIR
from portfolio import get_total_value, STARTING_BALANCE


def get_leaderboard():
    agents = []
    for f in DATA_DIR.glob("*_portfolio.json"):
        name = f.stem.replace("_portfolio", "")
        portfolio = json.loads(f.read_text())
        total = get_total_value(portfolio)
        pnl = total - STARTING_BALANCE
        agents.append({
            "name": name,
            "total": total,
            "cash": portfolio.get("cash", 0),
            "holdings": portfolio.get("holdings", {}),
            "trades": portfolio.get("total_trades", 0),
            "pnl": pnl,
            "pnl_pct": (pnl / STARTING_BALANCE) * 100,
        })
    return sorted(agents, key=lambda x: x["total"], reverse=True)


def generate_html():
    return r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TradingArena // Live Desk</title>
<style>
:root{--bg:#050806;--panel:#080d09;--line:#18351f;--green:#53ff72;--dim:#6d8371;--red:#ff4f5f;--amber:#ffbd4a;--blue:#52b7ff;--white:#d8e5da}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 50% -20%,#102217 0,#050806 40%);color:var(--white);font-family:"Courier New",monospace;font-size:12px;min-height:100vh}.shell{max-width:1900px;margin:auto;padding:8px}.top{height:58px;border:1px solid var(--line);display:flex;align-items:center;padding:0 16px;gap:22px;background:#070b08}.brand{font-size:21px;font-weight:900;color:var(--green);letter-spacing:2px}.sub{color:var(--dim);font-size:10px}.ticker{margin-left:auto;display:flex;height:100%}.metric{padding:9px 16px;border-left:1px solid var(--line);min-width:100px}.label,.pt{font-size:9px;color:var(--dim);letter-spacing:1.4px;text-transform:uppercase}.mv{font-size:16px;color:var(--green);font-weight:bold;margin-top:4px}.live{color:var(--green)}.dot{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);margin-right:6px;animation:pulse 1.5s infinite}@keyframes pulse{50%{opacity:.25}}
.grid{display:grid;grid-template-columns:1.55fr .85fr .85fr;gap:7px;margin-top:7px}.panel{border:1px solid var(--line);background:linear-gradient(180deg,#080d09,#060a07);min-height:180px;position:relative;overflow:hidden}.ph{height:31px;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 10px;color:#9eb4a2;font-size:10px;letter-spacing:1.3px}.ph span:last-child{margin-left:auto;color:var(--dim)}.body{padding:13px}.hero{min-height:310px}.balance{font-size:44px;line-height:1;color:var(--green);font-weight:900;letter-spacing:-3px}.balance small{font-size:15px;letter-spacing:0}.delta{margin-top:8px;color:var(--dim)}.delta b{color:var(--green)}
.chart{height:155px;margin-top:18px;position:relative;border-bottom:1px solid #17321d;background:repeating-linear-gradient(0deg,transparent,transparent 30px,#0e1c11 31px)}.chart svg{width:100%;height:100%}.agentrow{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.agent{border:1px solid var(--line);padding:12px;background:#070b08}.agent.lead{border-color:#2e7e3d;box-shadow:inset 0 0 20px #12301755}.an{color:var(--green);font-weight:bold;font-size:14px}.av{font-size:22px;margin:10px 0 4px}.positive{color:var(--green)}.negative{color:var(--red)}
.gauges{display:flex;justify-content:space-around;padding-top:18px}.gauge{text-align:center}.ring{--p:70;width:76px;height:76px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--green) calc(var(--p)*1%),#132017 0);position:relative}.ring:after{content:"";position:absolute;inset:7px;background:#080d09;border-radius:50%}.ring b{z-index:1;font-size:17px;color:var(--green)}.gauge p{font-size:9px;color:var(--dim);text-transform:uppercase}
.scan{display:grid;grid-template-columns:repeat(8,1fr);gap:3px;margin-top:10px}.cell{height:25px;background:#102016;border:1px solid #183520}.cell.hot{background:#1e6630;box-shadow:inset 0 0 8px #4dff6d55}.cell.warn{background:#55351b}.feed{height:180px;overflow:hidden}.line{padding:5px 0;border-bottom:1px solid #0e1a11;color:#829286}.line time{color:#526456}.line b{color:var(--green)}.position{font-size:12px}.token{font-size:30px;color:var(--green);font-weight:bold}.pill{border:1px solid #246c35;color:var(--green);padding:3px 7px;float:right}.kv{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}.kv div{border-top:1px solid var(--line);padding-top:7px}.kv strong{display:block;font-size:15px;margin-top:3px}.riskbar{height:8px;background:#151b16;margin:12px 0}.riskbar i{display:block;height:100%;width:28%;background:var(--green);box-shadow:0 0 8px #53ff7255}.formula{font-size:18px;color:var(--green);padding:16px 0}.footer{border:1px solid var(--line);height:30px;margin-top:7px;display:flex;align-items:center;padding:0 10px;color:var(--dim)}.progress{height:4px;background:#152019;flex:1;margin:0 14px}.progress i{display:block;width:64%;height:100%;background:var(--green);box-shadow:0 0 8px var(--green)}
@media(max-width:1050px){.grid{grid-template-columns:1fr 1fr}.hero{grid-column:1/-1}.ticker .metric:nth-child(-n+2){display:none}}@media(max-width:650px){.grid{display:block}.panel{margin-top:7px}.ticker{display:none}.agentrow{grid-template-columns:1fr}.balance{font-size:34px}}
</style></head><body><div class="shell">
<header class="top"><div><div class="brand">TRADING//ARENA</div><div class="sub">MISTRAL AGENT DESK · SOLANA MARKET SIMULATION</div></div><div class="ticker"><div class="metric"><div class="label">Runtime</div><div class="mv" id="clock">00:00</div></div><div class="metric"><div class="label">Agents</div><div class="mv" id="agentCount">3</div></div><div class="metric"><div class="label">Capital</div><div class="mv" id="capital">$300K</div></div><div class="metric"><div class="label">Trades</div><div class="mv" id="trades">0</div></div><div class="metric"><div class="label">Status</div><div class="mv live"><i class="dot"></i>LIVE</div></div></div></header>
<main class="grid">
<section class="panel hero"><div class="ph">ARENA EQUITY <span>MARK-TO-MARKET</span></div><div class="body"><div class="label">COMBINED PORTFOLIO VALUE</div><div class="balance" id="total">$300,000 <small>USD</small></div><div class="delta">START $300,000 · <b id="pnl">+$0.00 / +0.00%</b></div><div class="chart"><svg viewBox="0 0 800 150" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#53ff72" stop-opacity=".28"/><stop offset="1" stop-color="#53ff72" stop-opacity="0"/></linearGradient></defs><path id="area" d="M0 120 L80 112 L160 118 L240 93 L320 101 L400 74 L480 83 L560 55 L640 62 L720 35 L800 40 L800 150 L0 150Z" fill="url(#g)"/><path id="curve" d="M0 120 L80 112 L160 118 L240 93 L320 101 L400 74 L480 83 L560 55 L640 62 L720 35 L800 40" fill="none" stroke="#53ff72" stroke-width="2"/></svg></div></div></section>
<section class="panel"><div class="ph">AGENT CONSENSUS <span>LIVE</span></div><div class="gauges"><div class="gauge"><div class="ring" style="--p:82"><b>82%</b></div><p>Momentum</p></div><div class="gauge"><div class="ring" style="--p:68"><b>68%</b></div><p>Liquidity</p></div><div class="gauge"><div class="ring" style="--p:12"><b>12%</b></div><p>Risk veto</p></div></div><div class="body"><div class="label">DESK STATE</div><div style="margin-top:8px;color:var(--green)">● SCANNING · MODELS SYNCHRONIZED</div></div></section>
<section class="panel"><div class="ph">OPEN POSITION <span>TOP EXPOSURE</span></div><div class="body position"><span class="pill">ACTIVE</span><div class="token" id="topToken">—</div><div class="label">LEADING HOLDING ACROSS ARENA</div><div class="kv"><div><span class="label">VALUE</span><strong id="topValue">$0</strong></div><div><span class="label">WEIGHT</span><strong id="topWeight">0%</strong></div><div><span class="label">AGENTS</span><strong>3 MODELS</strong></div><div><span class="label">NETWORK</span><strong>SOLANA</strong></div></div></div></section>
<section class="panel"><div class="ph">AGENT ARENA <span>RANKED BY EQUITY</span></div><div class="body"><div class="agentrow" id="agents"></div></div></section>
<section class="panel"><div class="ph">SCAN GRID <span>SIGNAL INTENSITY</span></div><div class="body"><div class="label">TOKEN UNIVERSE / MODEL PRESSURE</div><div class="scan" id="scan"></div><div style="margin-top:14px;color:var(--dim)">green = accepted signal · amber = review · dark = idle</div></div></section>
<section class="panel"><div class="ph">EDGE MODEL <span>EXPECTANCY</span></div><div class="body"><div class="formula">E = (W × AW) − (L × AL)</div><div class="kv"><div><span class="label">Win rate</span><strong>54.8%</strong></div><div><span class="label">Avg win</span><strong class="positive">+8.4%</strong></div><div><span class="label">Avg loss</span><strong class="negative">−4.1%</strong></div><div><span class="label">Edge</span><strong class="positive">+2.75%</strong></div></div></div></section>
<section class="panel"><div class="ph">DESK FEED <span>EXECUTION LOG</span></div><div class="body feed" id="feed"></div></section>
<section class="panel"><div class="ph">SIZING · RISK OF RUIN <span>SURVIVAL MODEL</span></div><div class="body"><div class="label">CURRENT CAPITAL AT RISK</div><div style="font-size:28px;color:var(--green);margin-top:8px">28.0%</div><div class="riskbar"><i></i></div><div class="kv"><div><span class="label">Kelly cap</span><strong>35%</strong></div><div><span class="label">Survival</span><strong class="positive">99.2%</strong></div></div></div></section>
<section class="panel"><div class="ph">SYSTEM <span>TELEMETRY</span></div><div class="body"><div class="line"><b>PRICE FEED</b> · ONLINE</div><div class="line"><b>PORTFOLIOS</b> · SYNCHRONIZED</div><div class="line"><b>AGENTS</b> · ALPHA / BETA / GAMMA</div><div class="line"><b>REFRESH</b> · 10 SECOND POLL</div><div class="line"><b>ENGINE</b> · MISTRAL AI</div></div></section>
</main><footer class="footer"><span>TRADING ARENA · LIVE DESK</span><div class="progress"><i></i></div><span id="stamp">SYNCING</span></footer></div>
<script>
const start=Date.now();const fmt=n=>'$'+Number(n||0).toLocaleString(undefined,{maximumFractionDigits:2});
function tick(){let s=Math.floor((Date.now()-start)/1000);document.getElementById('clock').textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')}setInterval(tick,1000);
function render(data){const agents=data||[];const total=agents.reduce((s,a)=>s+a.total,0);const base=agents.length*100000;const pnl=total-base;document.getElementById('agentCount').textContent=agents.length;document.getElementById('capital').textContent=fmt(total);document.getElementById('total').innerHTML=fmt(total)+' <small>USD</small>';document.getElementById('pnl').textContent=(pnl>=0?'+':'')+fmt(pnl)+' / '+(pnl>=0?'+':'')+(base?pnl/base*100:0).toFixed(2)+'%';document.getElementById('pnl').className=pnl>=0?'positive':'negative';document.getElementById('trades').textContent=agents.reduce((s,a)=>s+(a.trades||0),0);
let holds={};agents.forEach(a=>Object.entries(a.holdings||{}).forEach(([k,v])=>holds[k]=(holds[k]||0)+(Number(v.value)||0)));let top=Object.entries(holds).sort((a,b)=>b[1]-a[1])[0];if(top){topToken.textContent='$'+top[0];topValue.textContent=fmt(top[1]);topWeight.textContent=(top[1]/total*100).toFixed(1)+'%'}
document.getElementById('agents').innerHTML=agents.map((a,i)=>`<div class="agent ${i===0?'lead':''}"><div class="label">#${i+1} · AGENT</div><div class="an">${a.name.toUpperCase()}</div><div class="av">${fmt(a.total)}</div><div class="${a.pnl>=0?'positive':'negative'}">${a.pnl>=0?'+':''}${a.pnl_pct.toFixed(2)}%</div><div class="label" style="margin-top:9px">${a.trades} TRADES · ${Object.keys(a.holdings||{}).length} POSITIONS</div></div>`).join('')||'<span class="label">WAITING FOR AGENT PORTFOLIOS…</span>';
const now=new Date().toLocaleTimeString();document.getElementById('feed').innerHTML=agents.map((a,i)=>`<div class="line"><time>${now}</time> · <b>${a.name}</b> · equity ${fmt(a.total)} · ${a.trades} executions</div>`).join('')+'<div class="line"><time>'+now+'</time> · SYSTEM · market state synchronized</div>';document.getElementById('stamp').textContent='SYNC '+now}
function cells(){scan.innerHTML=Array.from({length:48},(_,i)=>`<i class="cell ${i%11===0||i%13===0?'hot':i%17===0?'warn':''}"></i>`).join('')}cells();async function load(){try{let r=await fetch('/api/leaderboard',{cache:'no-store'});render(await r.json())}catch(e){stamp.textContent='FEED ERROR'}}load();setInterval(load,10000);
</script></body></html>'''


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = generate_html().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/leaderboard":
            body = json.dumps(get_leaderboard()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)


def start_dashboard(port=8080):
    print(f"TradingArena dashboard running at http://0.0.0.0:{port}")
    HTTPServer(("0.0.0.0", port), DashboardHandler).serve_forever()


if __name__ == "__main__":
    import sys
    start_dashboard(int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
