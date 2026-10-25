from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "/app/data/app.db"

os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, content FROM notes")
    notes = [{"id": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(notes)

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    content = data.get('content')
    if not content: return jsonify({"error": "Content is required"}), 400
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route('/api/ransomware', methods=['POST'])
def ransomware():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM notes")
    conn.commit()
    conn.close()
    return jsonify({"status": "wiped"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecoverX | Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #050505;
            --panel: rgba(10, 15, 30, 0.7);
            --border: rgba(0, 255, 255, 0.3);
            --cyan: #00ffff;
            --danger: #ff003c;
            --success: #00ff66;
            --text: #e0e0e0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Share Tech Mono', monospace; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; padding: 20px; overflow-x: hidden; }
        
        .grid-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
                   background-image: linear-gradient(rgba(0,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,255,0.05) 1px, transparent 1px); 
                   background-size: 30px 30px; z-index: -1; }

        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 15px; margin-bottom: 30px; }
        .header h1 { color: var(--cyan); text-shadow: 0 0 10px var(--cyan); font-size: 24px; letter-spacing: 2px; }
        .status { color: var(--success); animation: blink 2s infinite; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

        .layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        
        .panel { background: var(--panel); backdrop-filter: blur(10px); border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.05); }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; background: rgba(0,0,0,0.5); border: 1px solid var(--border); color: var(--cyan); outline: none; }
        input:focus { border-color: var(--cyan); box-shadow: 0 0 10px rgba(0,255,255,0.3); }
        button { padding: 12px 20px; background: transparent; border: 1px solid var(--cyan); color: var(--cyan); cursor: pointer; text-transform: uppercase; transition: 0.2s; }
        button:hover { background: var(--cyan); color: var(--bg); }

        .data-stream { display: flex; flex-direction: column; gap: 10px; }
        .data-node { background: rgba(0, 255, 255, 0.05); border-left: 3px solid var(--cyan); padding: 15px; display: flex; justify-content: space-between; align-items: center; animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { transform: translateX(-20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        
        .danger-zone { border-color: var(--danger); box-shadow: 0 0 20px rgba(255, 0, 60, 0.1); }
        .danger-title { color: var(--danger); text-shadow: 0 0 10px var(--danger); margin-bottom: 15px; font-size: 18px; }
        .danger-btn { width: 100%; border-color: var(--danger); color: var(--danger); padding: 20px; font-size: 18px; font-weight: bold; }
        .danger-btn:hover { background: var(--danger); color: white; box-shadow: 0 0 20px var(--danger); }
        .log { margin-top: 20px; font-size: 12px; color: var(--text); opacity: 0.7; height: 150px; overflow-y: auto; }

        .glitch { animation: glitchAnim 0.5s linear infinite; }
        @keyframes glitchAnim {
            0% { transform: translate(0); }
            20% { transform: translate(-5px, 5px); text-shadow: 2px 0 red, -2px 0 blue; }
            40% { transform: translate(-5px, -5px); text-shadow: 2px 0 red, -2px 0 blue; }
            60% { transform: translate(5px, 5px); text-shadow: 2px 0 red, -2px 0 blue; }
            80% { transform: translate(5px, -5px); text-shadow: 2px 0 red, -2px 0 blue; }
            100% { transform: translate(0); }
        }
    </style>
</head>
<body>
    <div class="grid-bg"></div>

    <div class="header">
        <h1>🛡️ RecoverX // DATA VAULT</h1>
        <div>SYSTEM STATUS: <span class="status">ONLINE</span></div>
    </div>

    <div class="layout">
        <div class="panel" id="mainPanel">
            <h2 style="margin-bottom: 20px; color: var(--cyan);">SECURE TRANSMISSION</h2>
            <div class="input-group">
                <input type="text" id="noteInput" placeholder="Enter encrypted payload..." onkeypress="if(event.key === 'Enter') addNote()">
                <button onclick="addNote()">Transmit</button>
            </div>
            <div class="data-stream" id="notesList">
                <!-- Notes will load here -->
            </div>
        </div>

        <div class="panel danger-zone">
            <div class="danger-title">WORM BACKUP PROTOCOL</div>
            <p style="font-size: 12px; margin-bottom: 20px; opacity: 0.8;">
                Live data is automatically synchronized to a MinIO S3 bucket with Object Lock (Compliance Mode). 
                This ensures immutability against ransomware.
            </p>
            <button class="danger-btn" onclick="simulateRansomware()">⚠ INITIATE RANSOMWARE</button>
            
            <div class="log" id="consoleLog">
                > SYSTEM READY<br>
                > WORM PROTECTION: ACTIVE<br>
                > AWAITING INPUT...
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/api/notes';
        const consoleLog = document.getElementById('consoleLog');

        function log(msg, color = 'var(--cyan)') {
            const p = document.createElement('div');
            p.innerHTML = `> ${msg}`;
            p.style.color = color;
            consoleLog.appendChild(p);
            consoleLog.scrollTop = consoleLog.scrollHeight;
        }

        async function fetchNotes() {
            const res = await fetch(API_URL);
            const notes = await res.json();
            const list = document.getElementById('notesList');
            list.innerHTML = '';
            
            notes.forEach(note => {
                const div = document.createElement('div');
                div.className = 'data-node';
                div.innerHTML = `<span>${note.content}</span><span style="font-size:10px; opacity:0.5;">ID: ${note.id}</span>`;
                list.appendChild(div);
            });
        }

        async function addNote() {
            const input = document.getElementById('noteInput');
            const content = input.value.trim();
            if (!content) return;
            
            log("ENCRYPTING AND TRANSMITTING...", "var(--success)");
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            input.value = '';
            log("TRANSMISSION SECURED.", "var(--success)");
            fetchNotes();
        }

        async function simulateRansomware() {
            log("⚠ WARNING: MALWARE DETECTED", "var(--danger)");
            log("DELETING LIVE DATABASE...", "var(--danger)");
            
            document.getElementById('mainPanel').classList.add('glitch');

            await fetch('/api/ransomware', { method: 'POST' });
            
            setTimeout(() => {
                document.getElementById('mainPanel').classList.remove('glitch');
                fetchNotes(); 
                log("LIVE DATA DESTROYED. SYSTEM OFFLINE.", "var(--danger)");
                log("ATTEMPTING WORM RECOVERY...", "yellow");
                
                setTimeout(() => {
                    log("CONTACTING MINIO VAULT...", "yellow");
                    setTimeout(() => {
                        log("RESTORE SUCCESSFUL. DATA RECOVERED.", "var(--success)");
                        alert("To complete the drill, run ~/recoverx-restore.sh in your terminal!");
                        fetchNotes();
                    }, 1500);
                }, 1500);
            }, 1000);
        }

        fetchNotes();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
