"""
Dashboard — Simple web leaderboard for trading agents
"""
import json
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

from config import DATA_DIR
from portfolio import get_portfolio, get_total_value, STARTING_BALANCE


def get_leaderboard() -> list:
    """Get all agents sorted by portfolio value."""
    agents = []
    for f in DATA_DIR.glob("*_portfolio.json"):
        name = f.stem.replace("_portfolio", "")
        portfolio = json.loads(f.read_text())
        total = get_total_value(portfolio)
        pnl = total - STARTING_BALANCE
        pnl_pct = (pnl / STARTING_BALANCE) * 100
        
        agents.append({
            "name": name,
            "total": total,
            "cash": portfolio["cash"],
            "holdings": len(portfolio.get("holdings", {})),
            "trades": portfolio.get("total_trades", 0),
            "pnl": pnl,
            "pnl_pct": pnl_pct,
        })
    
    return sorted(agents, key=lambda x: x["total"], reverse=True)


def generate_html() -> str:
    """Generate dashboard HTML."""
    leaderboard = get_leaderboard()
    
    rows = ""
    for i, agent in enumerate(leaderboard, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        pnl_color = "green" if agent["pnl"] >= 0 else "red"
        rows += f"""
        <tr>
            <td>{medal}</td>
            <td><strong>{agent['name']}</strong></td>
            <td>${agent['total']:,.2f}</td>
            <td style="color:{pnl_color}">{'+' if agent['pnl'] >= 0 else ''}{agent['pnl']:.2f} ({agent['pnl_pct']:+.1f}%)</td>
            <td>${agent['cash']:,.2f}</td>
            <td>{agent['holdings']}</td>
            <td>{agent['trades']}</td>
        </tr>
        """
    
    if not leaderboard:
        rows = '<tr><td colspan="7" style="text-align:center">No agents yet. Run: python agent.py &lt;name&gt;</td></tr>'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Crypto Trading Arena</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }}
        h1 {{ text-align: center; color: #00ff88; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: #111; border-radius: 10px; overflow: hidden; }}
        th {{ background: #1a1a1a; padding: 15px; text-align: left; color: #00ff88; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #222; }}
        tr:hover {{ background: #1a1a1a; }}
        .timestamp {{ text-align: center; color: #555; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>Crypto Trading Arena</h1>
    <p class="subtitle">AI Agents competing with $100K each</p>
    
    <table>
        <thead>
            <tr>
                <th>Rank</th>
                <th>Agent</th>
                <th>Portfolio Value</th>
                <th>PnL</th>
                <th>Cash</th>
                <th>Holdings</th>
                <th>Trades</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    
    <p class="timestamp">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>"""
    
    return html


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(generate_html().encode())
        elif self.path == "/api/leaderboard":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_leaderboard(), indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()


def start_dashboard(port=8080):
    """Start the dashboard server."""
    print(f"Dashboard running at http://localhost:{port}")
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_dashboard(port)
