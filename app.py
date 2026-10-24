from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "/app/data/app.db"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)")
    conn.commit()
    conn.close()


init_db()


@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT id, content FROM notes ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id": row[0], "content": row[1]} for row in rows])


@app.route('/api/notes', methods=['POST'])
def add_note():
    content = (request.json or {}).get('content', '').strip()
    if not content:
        return jsonify({"error": "Content is required"}), 400
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201


@app.route('/api/ransomware', methods=['POST'])
def ransomware():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM notes")
    conn.commit()
    conn.close()
    return jsonify({"status": "wiped"})


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


BASE_HEAD = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ title }} | RecoverX</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config={theme:{extend:{colors:{ink:'#0b1120',cyanx:'#06b6d4'}}}}</script>
</head>
<body class="min-h-screen bg-[#0b1120] text-white antialiased">
'''

LANDING = BASE_HEAD + '''
<main class="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-16">
  <div class="pointer-events-none absolute left-1/2 top-0 h-[520px] w-[780px] -translate-x-1/2 rounded-full bg-cyan-500/10 blur-3xl"></div>
  <section class="relative max-w-3xl text-center">
    <div class="mx-auto mb-8 flex h-16 w-16 items-center justify-center rounded-2xl border border-cyan-400/30 bg-cyan-400/10 shadow-[0_0_40px_rgba(6,182,212,.18)]">
      <svg class="h-8 w-8 text-cyan-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></svg>
    </div>
    <p class="mb-4 text-xs font-semibold uppercase tracking-[.28em] text-cyan-300">Data resilience infrastructure</p>
    <h1 class="text-5xl font-semibold tracking-tight sm:text-7xl"><span class="bg-gradient-to-r from-cyan-300 via-sky-400 to-blue-500 bg-clip-text text-transparent">RecoverX Platform</span></h1>
    <p class="mt-6 text-xl font-medium text-slate-200 sm:text-2xl">Immutable Protection. Verified Recovery.</p>
    <p class="mx-auto mt-5 max-w-xl text-base leading-7 text-slate-400">Protect critical workloads with immutable backups, continuous verification, and recovery workflows designed for the moment resilience matters most.</p>
    <a href="/login" class="mt-10 inline-flex items-center gap-3 rounded-lg bg-cyan-400 px-6 py-3.5 text-sm font-bold text-slate-950 shadow-lg shadow-cyan-500/20 transition hover:bg-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 focus:ring-offset-[#0b1120]">Access Dashboard <span aria-hidden="true">→</span></a>
    <div class="mt-16 flex items-center justify-center gap-6 text-xs text-slate-500"><span>WORM storage</span><span class="h-1 w-1 rounded-full bg-slate-600"></span><span>Continuous verification</span><span class="h-1 w-1 rounded-full bg-slate-600"></span><span>Rapid recovery</span></div>
  </section>
</main>
</body></html>'''

LOGIN = BASE_HEAD + '''
<main class="flex min-h-screen items-center justify-center px-6 py-16">
  <section class="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/70 p-8 shadow-2xl shadow-cyan-950/20 backdrop-blur-xl">
    <a href="/" class="mb-8 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyan-300">← Back to RecoverX</a>
    <div class="mb-8"><p class="text-xs font-semibold uppercase tracking-[.2em] text-cyan-300">Secure access</p><h1 class="mt-2 text-3xl font-semibold">Sign in to dashboard</h1><p class="mt-2 text-sm text-slate-400">Use the demo access code to enter the recovery console.</p></div>
    <form onsubmit="event.preventDefault(); window.location='/dashboard'" class="space-y-5"><label class="block text-sm font-medium text-slate-300" for="email">Work email<input id="email" type="email" required placeholder="admin@recoverx.io" class="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-3 text-white outline-none placeholder:text-slate-600 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"></label><button class="w-full rounded-lg bg-cyan-400 px-4 py-3 font-bold text-slate-950 transition hover:bg-cyan-300">Continue to dashboard</button></form>
  </section>
</main>
</body></html>'''

DASHBOARD = BASE_HEAD + '''
<div class="flex min-h-screen flex-col md:flex-row">
  <aside class="flex w-full shrink-0 flex-col border-b border-slate-800 bg-slate-950/70 p-5 md:w-64 md:border-b-0 md:border-r">
    <a href="/" class="flex items-center gap-3"><span class="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-300"><svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3 20 6v5c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6l8-3Z"/><path d="m8.5 12 2.2 2.2 4.8-5"/></svg></span><span class="text-lg font-semibold">Recover<span class="text-cyan-300">X</span></span></a>
    <nav class="mt-10 space-y-1" aria-label="Primary navigation"><a class="flex items-center gap-3 rounded-lg bg-cyan-400/10 px-3 py-2.5 text-sm font-medium text-cyan-300" href="/dashboard">Dashboard</a><a class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 hover:bg-slate-800 hover:text-white" href="#backups">Backups</a><a class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-400 hover:bg-slate-800 hover:text-white" href="#recovery">Recovery</a></nav>
    <a href="/" class="mt-auto hidden items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-500 hover:bg-slate-800 hover:text-white md:flex">Log out</a>
  </aside>
  <main class="flex-1 overflow-y-auto p-5 sm:p-8"><header class="flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between"><div><p class="text-xs font-semibold uppercase tracking-[.2em] text-slate-500">RecoverX / Operations</p><h1 class="mt-2 text-2xl font-semibold tracking-tight sm:text-3xl">System Overview</h1></div><div class="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-sm font-medium text-emerald-300"><span class="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]"></span>Cluster Healthy</div></header>
    <section class="grid gap-4 py-6 sm:grid-cols-2 xl:grid-cols-4"><div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5"><p class="text-xs uppercase tracking-wider text-slate-500">Recovery Point</p><p class="mt-3 text-2xl font-semibold">&lt; 5 mins</p><p class="mt-1 text-xs text-emerald-300">Within target</p></div><div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5"><p class="text-xs uppercase tracking-wider text-slate-500">Recovery Time</p><p class="mt-3 text-2xl font-semibold text-cyan-300">~ 10 sec</p><p class="mt-1 text-xs text-slate-500">Last verified today</p></div><div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5"><p class="text-xs uppercase tracking-wider text-slate-500">WORM Protection</p><p class="mt-3 flex items-center gap-2 text-2xl font-semibold"><span class="text-cyan-300">●</span> Active</p><p class="mt-1 text-xs text-slate-500">Immutable policy enforced</p></div><div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5"><p class="text-xs uppercase tracking-wider text-slate-500">Database Status</p><p class="mt-3 flex items-center gap-2 text-2xl font-semibold"><span class="text-emerald-400">●</span> Connected</p><p class="mt-1 text-xs text-emerald-300">Live sync enabled</p></div></section>
    <section class="grid gap-5 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,1fr)]"><div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5 sm:p-6"><div class="flex items-center justify-between"><div><h2 class="text-lg font-semibold">Live Database</h2><p class="mt-1 text-sm text-slate-500">Protected application records</p></div><span class="rounded-md border border-slate-700 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">SQLite</span></div><div class="mt-6 flex flex-col gap-3 sm:flex-row"><label class="sr-only" for="noteInput">New record</label><input id="noteInput" onkeydown="if(event.key==='Enter' && !event.nativeEvent?.isComposing) addNote()" placeholder="Add a new record..." class="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-400"><button onclick="addNote()" class="rounded-lg bg-cyan-400 px-5 py-3 text-sm font-bold text-slate-950 transition hover:bg-cyan-300">Save record</button></div><div id="notesList" class="mt-5 space-y-2" aria-live="polite"><p class="rounded-lg border border-dashed border-slate-800 p-5 text-center text-sm text-slate-500">Loading protected records...</p></div></div><div class="rounded-xl border border-red-500/30 bg-red-950/10 p-5 sm:p-6"><div class="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10 text-red-400"><span class="text-xl">!</span></div><h2 class="mt-5 text-lg font-semibold text-red-200">Ransomware Simulator</h2><p class="mt-2 text-sm leading-6 text-slate-400">Simulate a data-loss event against the live database. This destructive action clears records so recovery controls can be tested.</p><button id="attackBtn" onclick="simulateRansomware()" class="mt-6 w-full rounded-lg border border-red-500/60 bg-red-500/10 px-4 py-3 text-sm font-bold text-red-300 transition hover:bg-red-500 hover:text-white">Wipe Database</button><p id="simStatus" class="mt-3 text-center text-xs text-slate-600">Simulation controls are isolated to this environment.</p></div></section>
  </main>
</div>
<script>
async function fetchNotes(){const r=await fetch('/api/notes');const notes=await r.json();const list=document.getElementById('notesList');list.innerHTML=notes.length?notes.map(n=>`<div class="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-3"><span class="text-sm text-slate-200"></span><span class="text-xs text-slate-600">#${n.id}</span></div>`).join(''):'<p class="rounded-lg border border-dashed border-slate-800 p-5 text-center text-sm text-slate-500">No protected records found.</p>';notes.forEach((n,i)=>list.children[i].querySelector('span').textContent=n.content)}
async function addNote(){const input=document.getElementById('noteInput');const content=input.value.trim();if(!content)return;await fetch('/api/notes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content})});input.value='';fetchNotes()}
async function simulateRansomware(){const button=document.getElementById('attackBtn');button.disabled=true;button.textContent='Wiping database...';await fetch('/api/ransomware',{method:'POST'});document.getElementById('simStatus').textContent='Database wiped. Recovery verification required.';button.textContent='Database wiped';fetchNotes()}
fetchNotes();
</script>
</body></html>'''


@app.route('/')
def index():
    return render_template_string(LANDING, title='Immutable Protection')


@app.route('/login')
def login():
    return render_template_string(LOGIN, title='Secure Access')


@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD, title='System Overview')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
