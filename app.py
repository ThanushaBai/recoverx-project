from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import datetime

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

# --- API ROUTES ---
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

# --- FRONTEND (RecoverX Platform) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecoverX | Immutable Protection</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0b1120;
            --panel: rgba(30, 41, 59, 0.7);
            --border: rgba(255, 255, 255, 0.1);
            --cyan: #06b6d4;
            --danger: #ef4444;
            --success: #10b981;
            --text: #f8fafc;
            --muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }
        body { background: var(--bg); color: var(--text); min-height: 100vh; }

        /* --- LANDING PAGE --- */
        #landing-page { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center; background: radial-gradient(circle at top, #1e293b 0%, #0b1120 100%); }
        #landing-page h1 { font-size: 56px; font-weight: 700; margin-bottom: 20px; background: linear-gradient(to right, #06b6d4, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        #landing-page p { font-size: 20px; color: var(--muted); max-width: 600px; margin-bottom: 40px; line-height: 1.6; }
        .btn-primary { background: var(--cyan); color: #000; padding: 15px 40px; border-radius: 8px; font-weight: 600; text-decoration: none; cursor: pointer; transition: 0.2s; border: none; font-size: 18px; }
        .btn-primary:hover { background: #22d3ee; box-shadow: 0 0 20px rgba(6, 182, 212, 0.4); }

        /* --- AUTH MODAL --- */
        #auth-modal { display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); align-items: center; justify-content: center; z-index: 100; }
        .auth-box { background: var(--panel); border: 1px solid var(--border); padding: 40px; border-radius: 16px; width: 100%; max-width: 400px; text-align: center; }
        .auth-box input { width: 100%; padding: 12px; margin: 20px 0; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 8px; color: white; outline: none; }

        /* --- DASHBOARD --- */
        #dashboard { display: none; height: 100vh; overflow: hidden; }
        .nav { width: 250px; background: var(--panel); border-right: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; }
        .nav-brand { font-size: 24px; font-weight: 700; color: var(--cyan); margin-bottom: 40px; display: flex; align-items: center; gap: 10px;}
        .nav-item { padding: 12px 15px; color: var(--muted); border-radius: 8px; margin-bottom: 5px; cursor: pointer; font-weight: 500; }
        .nav-item:hover, .nav-item.active { background: rgba(6, 182, 212, 0.1); color: var(--cyan); }
        
        .main-content { flex: 1; padding: 30px; overflow-y: auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
        .card-title { font-size: 14px; color: var(--muted); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;}
        .card-value { font-size: 28px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        
        .split-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        
        /* Notes Section */
        .notes-section { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .input-group input { flex: 1; padding: 12px; background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 8px; color: white; outline: none; }
        .data-stream { display: flex; flex-direction: column; gap: 10px; max-height: 300px; overflow-y: auto;}
        .data-node { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 3px solid var(--cyan); }
        
        /* Ransomware Section */
        .danger-zone { border-color: rgba(239, 68, 68, 0.3); }
        .danger-btn { width: 100%; padding: 15px; background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid var(--danger); border-radius: 8px; font-weight: bold; cursor: pointer; margin-bottom: 10px;}
        .danger-btn:hover { background: var(--danger); color: white; }
        .restore-btn { width: 100%; padding: 15px; background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid var(--success); border-radius: 8px; font-weight: bold; cursor: pointer; display: none;}
        .restore-btn:hover { background: var(--success); color: white; }
    </style>
</head>
<body>

    <!-- 1. LANDING PAGE -->
    <div id="landing-page">
        <h1>RecoverX Platform</h1>
        <p>Immutable Protection. Verified Recovery. <br>The next-generation cloud-native data resilience platform powered by Kubernetes and WORM storage.</p>
        <button class="btn-primary" onclick="showAuth()">Access Dashboard</button>
    </div>

    <!-- 2. AUTH MODAL -->
    <div id="auth-modal">
        <div class="auth-box">
            <h2 style="margin-bottom: 10px;">Secure Login</h2>
            <p style="color: var(--muted); font-size: 14px;">Enter your email to receive a simulated access code.</p>
            <input type="email" id="emailInput" placeholder="admin@recoverx.io">
            <button class="btn-primary" style="width: 100%; padding: 12px;" onclick="sendCode()">Send Code</button>
        </div>
    </div>

    <!-- 3. DASHBOARD -->
    <div id="dashboard" style="display: none; flex-direction: row;">
        <!-- Sidebar -->
        <div class="nav">
            <div class="nav-brand">🛡️ RecoverX</div>
            <div class="nav-item active">Dashboard</div>
            <div class="nav-item">Backups</div>
            <div class="nav-item">Recovery</div>
            <div class="nav-item">Settings</div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <div class="header">
                <h1>System Overview</h1>
                <div style="color: var(--success); font-weight: 600;">● Cluster Healthy</div>
            </div>

            <!-- Stats -->
            <div class="stats-grid">
                <div class="card">
                    <div class="card-title">App Status</div>
                    <div class="card-value" style="color: var(--success);">● Running</div>
                </div>
                <div class="card">
                    <div class="card-title">Recovery Point (RPO)</div>
                    <div class="card-value">&lt; 5 mins</div>
                </div>
                <div class="card">
                    <div class="card-title">Recovery Time (RTO)</div>
                    <div class="card-value" style="color: var(--cyan);">~ 10 sec</div>
                </div>
                <div class="card">
                    <div class="card-title">WORM Protection</div>
                    <div class="card-value">🔒 Active</div>
                </div>
            </div>

            <div class="split-layout">
                <!-- Left: Data Input -->
                <div class="notes-section">
                    <h3 style="margin-bottom: 15px;">Live Database (SQLite)</h3>
                    <div class="input-group">
                        <input type="text" id="noteInput" placeholder="Add a new record..." onkeypress="if(event.key === 'Enter') addNote()">
                        <button class="btn-primary" style="padding: 12px 20px; font-size: 14px;" onclick="addNote()">Save</button>
                    </div>
                    <div class="data-stream" id="notesList"></div>
                </div>

                <!-- Right: Simulator -->
                <div class="card danger-zone">
                    <h3 style="color: var(--danger); margin-bottom: 15px;">Ransomware Simulator</h3>
                    <p style="font-size: 13px; color: var(--muted); margin-bottom: 20px;">Simulate a data-loss event. RecoverX will use MinIO WORM backups to restore the database.</p>
                    <button class="danger-btn" id="attackBtn" onclick="simulateRansomware()">⚠ Wipe Database</button>
                    <button class="restore-btn" id="restoreBtn" onclick="restoreData()">🛡 Restore Database</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_URL = '/api/notes';

        // Auth Logic
        function showAuth() { document.getElementById('auth-modal').style.display = 'flex'; }
        function sendCode() {
            const email = document.getElementById('emailInput').value;
            if (!email) return alert("Please enter an email.");
            alert("Simulated Code Sent to " + email + "! (Code is 123456)");
            const code = prompt("Enter the 6-digit code:");
            if (code === "123456") {
                document.getElementById('auth-modal').style.display = 'none';
                document.getElementById('landing-page').style.display = 'none';
                document.getElementById('dashboard').style.display = 'flex';
                fetchNotes();
            } else {
                alert("Invalid code.");
            }
        }

        // Data Logic
        async function fetchNotes() {
            const res = await fetch(API_URL);
            const notes = await res.json();
            const list = document.getElementById('notesList');
            list.innerHTML = '';
            if(notes.length === 0) list.innerHTML = '<p style="color: var(--muted); font-size: 14px;">No records found.</p>';
            notes.forEach(note => {
                const div = document.createElement('div');
                div.className = 'data-node';
                div.innerHTML = `<span>${note.content}</span>`;
                list.appendChild(div);
            });
        }

        async function addNote() {
            const input = document.getElementById('noteInput');
            const content = input.value.trim();
            if (!content) return;
            await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            input.value = '';
            fetchNotes();
        }

        async function simulateRansomware() {
            document.getElementById('dashboard').style.filter = 'hue-rotate(90deg) contrast(150%)';
            await fetch('/api/ransomware', { method: 'POST' });
            setTimeout(() => {
                document.getElementById('dashboard').style.filter = 'none';
                fetchNotes(); 
                document.getElementById('attackBtn').style.display = 'none';
                document.getElementById('restoreBtn').style.display = 'block';
            }, 1000);
        }

        async function restoreData() {
            document.getElementById('restoreBtn').innerText = "Restoring from MinIO...";
            setTimeout(() => {
                document.getElementById('restoreBtn').style.display = 'none';
                document.getElementById('attackBtn').style.display = 'block';
                document.getElementById('restoreBtn').innerText = "🛡 Restore Database";
                alert("Simulation complete! Run ~/recoverx-restore.sh in your terminal and refresh the page to see real data.");
                fetchNotes();
            }, 2000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
