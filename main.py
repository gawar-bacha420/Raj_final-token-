from flask import Flask, render_template_string, request, jsonify
import requests
import time
import threading
import secrets

app = Flask(__name__)

# Global storage for active tasks
tasks = {}

class MessengerAutomator:
    def __init__(self, task_id, stop_key, tokens, targets, messages, first_name, last_name, delay=5, target_type='inbox'):
        self.task_id = task_id
        self.stop_key = stop_key
        self.tokens = tokens
        self.targets = targets
        self.messages = messages
        self.first_name = first_name
        self.last_name = last_name
        self.delay = delay
        self.target_type = target_type
        self.running = True
        self.logs = []
        self.session = requests.Session()

    def add_log(self, message, log_type="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append({"time": timestamp, "msg": message, "type": log_type})

    def send_fb_message(self, token, target_id, message):
        try:
            url = f"https://graph.facebook.com/v17.0/me/messages?access_token={token}"
            payload = {
                "recipient": {"id": target_id},
                "message": {"text": message},
                "messaging_type": "MESSAGE_TAG",
                "tag": "CONFIRMED_EVENT_UPDATE"
            }
            response = self.session.post(url, json=payload)
            res_json = response.json()

            if "error" in res_json:
                url = f"https://graph.facebook.com/v17.0/t_{target_id}/"
                params = {'access_token': token, 'message': message}
                response = self.session.post(url, data=params)
                res_json = response.json()

                if "error" in res_json:
                    url = f"https://graph.facebook.com/v17.0/{target_id}/comments"
                    response = self.session.post(url, data=params)
                    res_json = response.json()

            return res_json
        except Exception as e:
            return {"error": str(e)}

    def run(self):
        self.add_log(f"🚀 Started. Stop Key: {self.stop_key}", "info")
        while True:
            for token in self.tokens:
                if not self.running: break
                for target_id in self.targets:
                    if not self.running: break
                    for msg_content in self.messages:
                        if not self.running: break
                        final_msg = f"{self.first_name} {msg_content} {self.last_name}"
                        try:
                            result = self.send_fb_message(token, target_id, final_msg)
                            if any(key in result for key in ["message_id", "id", "success"]):
                                self.add_log(f"✅ Sent: {final_msg[:20]}... to {target_id}", "sent")
                            elif "error" in result:
                                err = result["error"]
                                err_text = err.get('message', 'Error') if isinstance(err, dict) else str(err)
                                self.add_log(f"❌ {err_text}", "error")
                        except Exception as e:
                            self.add_log(f"❌ System: {str(e)}", "error")
                        time.sleep(self.delay)
            if not self.running: break
            time.sleep(2)

    def stop(self):
        self.running = False
        self.add_log("🛑 Stopped via Key.", "error")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>💎 R9J M9LTY OFFLINE CONVO 24/7 💎</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: url('https://i.postimg.cc/Xvf1RZWS/bb1dfb2eadbc22f0abeccef5594227de.jpg') no-repeat center center fixed !important;
            background-size: cover !important;
            color: #fff; margin: 0; padding: 10px; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh;
            overflow-x: hidden;
        }
        :root { 
            --neon-blue: #00d2ff;
            --neon-green: #39ff14;
            --neon-pink: #ff007f;
            --neon-gold: #ffd700;
            --neon-purple: #bc13fe;
        }
        @keyframes random-color {
            0% { color: #ff0000; text-shadow: 0 0 10px #ff0000; }
            20% { color: #ffff00; text-shadow: 0 0 10px #ffff00; }
            40% { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
            60% { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
            80% { color: #0000ff; text-shadow: 0 0 10px #0000ff; }
            100% { color: #ff00ff; text-shadow: 0 0 10px #ff00ff; }
        }
        .header-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 15px; border-radius: 20px; margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        h1 {
            font-weight: 800; margin: 0; text-transform: uppercase; font-size: 1.4rem;
            animation: random-color 1s infinite linear; letter-spacing: 2px;
        }
        .container {
            width: 100%; max-width: 450px; background: rgba(255, 255, 255, 0.03); 
            backdrop-filter: blur(20px); padding: 20px; border-radius: 30px; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); 
            text-align: center;
        }
        .input-group { 
            margin-bottom: 15px; padding: 15px; border-radius: 20px; 
            border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(255, 255, 255, 0.02);
            transition: 0.3s; backdrop-filter: blur(10px);
        }
        .input-group:hover { background: rgba(255, 255, 255, 0.05); border-color: rgba(255, 255, 255, 0.3); transform: translateY(-2px); }
        .group-token { border-color: #00d2ff; }
        .group-uid { border-color: #39ff14; }
        .group-name { border-color: #ff007f; }
        .group-delay { border-color: #ffd700; }
        .group-msg { border-color: #bc13fe; }
        label { display: block; margin-bottom: 5px; font-size: 0.8rem; text-align: left; font-weight: 800; color: #fff; text-transform: uppercase; }
        textarea, input, select {
            width: 100%; background: rgba(0, 0, 0, 0.6); border: 1px solid rgba(255, 255, 255, 0.3); 
            color: #fff; padding: 8px; border-radius: 8px; box-sizing: border-box; font-size: 0.8rem;
        }
        .btn-start { 
            width: 100%; padding: 12px; border-radius: 10px; font-weight: 900; cursor: pointer;
            background: linear-gradient(45deg, #ff007f, #bc13fe); color: #fff; border: none;
            box-shadow: 0 4px 15px rgba(255, 0, 127, 0.4); text-transform: uppercase; font-size: 0.9rem;
        }
        .token-status { 
            font-size: 0.75rem; margin-top: 5px; text-align: left; padding: 10px; 
            border-radius: 12px; background: rgba(0,0,0,0.4); border-left: 3px solid; 
            display: flex; align-items: center; gap: 10px;
        }
        .profile-pic { width: 40px; height: 40px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.2); }
        #logs {
            margin-top: 15px; background: rgba(0, 0, 0, 0.8); height: 140px;
            overflow-y: auto; padding: 10px; border-radius: 12px; font-family: 'Courier New', monospace;
            font-size: 0.7rem; text-align: left; border: 1px solid var(--neon-blue);
        }
        .log-entry { margin-bottom: 3px; border-left: 2px solid var(--neon-blue); padding-left: 6px; }
        .log-sent { color: #39ff14 !important; border-left-color: #39ff14 !important; }
        .log-error { color: #ff007f !important; border-left-color: #ff007f !important; }
        .btn-stop-area { margin-top: 15px; background: rgba(255, 0, 0, 0.1); border: 2px dashed var(--neon-pink); padding: 10px; border-radius: 12px; }
        .btn-stop { background: linear-gradient(45deg, #ff0000, #ff007f); border:none; padding: 10px; border-radius: 8px; color:#fff; width:100%; font-weight:900; cursor:pointer; text-transform:uppercase; font-size: 0.8rem; margin-top: 8px; }
        .hidden-group { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-box"><h1>💎 R9J M9LTY OFFLINE CONVO 24/7 💎</h1></div>

        <div class="input-group group-token">
            <label>🔍 TOKEN CHECKER (UNLIMITED) <i class="fas fa-search"></i></label>
            <select id="checkTokenOption" onchange="toggleCheckTokenInput()">
                <option value="paste">📝 Paste Tokens (Unlimited)</option>
                <option value="file">📁 Upload Token File</option>
            </select>
            <div id="checkTokenPasteArea" style="margin-top:10px;"><textarea id="checkTokens" rows="3" placeholder="Enter Tokens Line by Line"></textarea></div>
            <div id="checkTokenFileArea" class="hidden-group" style="margin-top:10px;"><input type="file" id="checkTokenFile"></div>
            <button class="btn-start" style="margin-top:10px; background: #00d2ff;" onclick="validateCheckTokens()">🚀 CHECK TOKENS</button>
            <div id="checkTokenResults" style="margin-top:10px; max-height:200px; overflow-y:auto;"></div>
        </div>

        <div class="input-group group-uid" style="background: rgba(57, 255, 20, 0.15);">
            <label>🔎 GROUP UID FETCHING <i class="fas fa-users"></i></label>
            <textarea id="fetchToken" rows="1" placeholder="Paste 1 Token to fetch groups..."></textarea>
            <button class="btn-start" style="margin-top:10px; background: #39ff14;" onclick="fetchGroups()">🔍 FETCH GROUP UIDs</button>
            <div id="groupFetchResults" style="margin-top:10px; max-height:200px; overflow-y:auto;"></div>
        </div>

        <div id="activeThreadKey" class="key-display hidden-group" style="background: rgba(188, 19, 254, 0.2); border: 2px solid var(--neon-purple); padding: 10px; border-radius: 12px; margin-bottom: 12px; font-weight: 800; color: #fff; font-size: 0.85rem;">
            🚀 STOP KEY: <span id="displayKey" style="color: var(--neon-gold);"></span>
        </div>

        <div class="input-group group-token">
            <label>🔑 Token Option 👈 <i class="fas fa-shield-alt"></i></label>
            <select id="tokenOption" onchange="toggleTokenInput()">
                <option value="paste">📝 Paste Tokens (Unlimited)</option>
                <option value="file">📁 Upload Token File</option>
            </select>
            <div id="tokenPasteArea" style="margin-top:10px;"><textarea id="tokens" rows="3" placeholder="Enter Tokens Line by Line"></textarea></div>
            <div id="tokenFileArea" class="hidden-group" style="margin-top:10px;"><input type="file" id="tokenFile"></div>
        </div>

        <div class="input-group group-uid">
            <label>💬 Target UID 🔎 <i class="fas fa-crosshairs"></i></label>
            <select id="targetType"><option value="inbox">📥 Inbox (Personal)</option><option value="group">👨‍👩‍👧‍👦 Group (Multi)</option></select>
            <textarea id="targets" rows="2" placeholder="Enter Target UIDs (One per line)" style="margin-top:10px;"></textarea>
        </div>

        <div class="input-group group-name"><label>👤 First Sender Name</label><input type="text" id="firstName" placeholder="e.g. Raj"></div>
        <div class="input-group group-name"><label>👤 Last Sender Name</label><input type="text" id="lastName" placeholder="e.g. Asiq"></div>
        <div class="input-group group-delay"><label>⏱️ Delay (Seconds)</label><input type="number" id="delay" value="5"></div>

        <div class="input-group group-msg">
            <label>📄 Message Box 🚀 <i class="fas fa-envelope-open-text"></i></label>
            <select id="msgOption" onchange="toggleMsgInput()"><option value="paste">📝 Paste Messages</option><option value="file">📁 Upload Msg File</option></select>
            <div id="msgPasteArea" style="margin-top:10px;"><textarea id="messages" rows="3" placeholder="Enter Messages (Line by Line)"></textarea></div>
            <div id="msgFileArea" class="hidden-group" style="margin-top:10px;"><input type="file" id="messageFile"></div>
        </div>

        <button class="btn-start" onclick="startAutomation()">🚀 VIEW / RUN FULL HD <i class="fas fa-play"></i></button>

        <div class="btn-stop-area">
            <label>🔐 STOP BOX (ENTER KEY)</label>
            <input type="text" id="stopKeyInput" placeholder="Paste stop key here...">
            <button class="btn-stop" onclick="stopAutomation()">🛑 STOP THREAD</button>
        </div>

        <div id="logs"><div class="log-entry" style="color: var(--neon-gold);">💎 SYSTEM READY 💎</div></div>
    </div>

    <script>
        let currentTaskId = null;
        let logInterval = null;

        function toggleTokenInput() {
            const isFile = document.getElementById('tokenOption').value === 'file';
            document.getElementById('tokenPasteArea').classList.toggle('hidden-group', isFile);
            document.getElementById('tokenFileArea').classList.toggle('hidden-group', !isFile);
        }

        function toggleMsgInput() {
            const isFile = document.getElementById('msgOption').value === 'file';
            document.getElementById('msgPasteArea').classList.toggle('hidden-group', isFile);
            document.getElementById('msgFileArea').classList.toggle('hidden-group', !isFile);
        }

        function toggleCheckTokenInput() {
            const isFile = document.getElementById('checkTokenOption').value === 'file';
            document.getElementById('checkTokenPasteArea').classList.toggle('hidden-group', isFile);
            document.getElementById('checkTokenFileArea').classList.toggle('hidden-group', !isFile);
        }

        async function validateCheckTokens() {
            const area = document.getElementById('checkTokenResults');
            let tokens = [];
            if (document.getElementById('checkTokenOption').value === 'paste') {
                tokens = document.getElementById('checkTokens').value.split('\\n').filter(t => t.trim());
            } else {
                const fileInput = document.getElementById('checkTokenFile');
                const file = fileInput.files[0];
                if (file) tokens = (await file.text()).split('\\n').filter(t => t.trim());
            }
            if (tokens.length === 0) { alert('Please enter tokens!'); return; }
            area.innerHTML = '';
            const colors = ['#00d2ff', '#39ff14', '#ff007f', '#ffd700', '#bc13fe'];
            
            for(let t of tokens) {
                const randomColor = colors[Math.floor(Math.random() * colors.length)];
                const row = document.createElement('div');
                row.className = 'token-status';
                row.style.borderLeft = '4px solid ' + randomColor;
                row.innerHTML = '<span style="color:' + randomColor + '">🔎 Processing...</span>';
                area.appendChild(row);

                try {
                    const response = await fetch('/api/check_token', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({token: t.trim()})
                    });
                    const data = await response.json();
                    if(data.name) {
                        row.innerHTML = '<img src="' + data.picture + '" class="profile-pic" onerror="this.src=\\'https://i.ibb.co/6P7S4nN/default-profile.png\\'"><div><span style="color:' + randomColor + '; font-weight:800;">✅ ' + data.name + '</span><br><small style="color:rgba(255,255,255,0.6)">Active 💎 | ID: ' + data.id + '</small></div>';
                    } else {
                        row.style.borderLeftColor = '#ff007f';
                        row.innerHTML = '<span style="color:#ff007f;">❌ ' + (data.error || 'Invalid Token') + '</span>';
                    }
                } catch(e) {
                    row.style.borderLeftColor = '#ff007f';
                    row.innerHTML = '<span style="color:#ff007f;">❌ Backend Error</span>';
                }
                area.scrollTop = area.scrollHeight;
            }
        }

        async function fetchGroups() {
            const area = document.getElementById('groupFetchResults');
            const tokenInput = document.getElementById('fetchToken').value.trim();
            if(!tokenInput) { alert('Paste a token first!'); return; }
            area.innerHTML = '<div class="token-status" style="color:#39ff14">🔎 Fetching Groups...</div>';
            const colors = ['#39ff14', '#00d2ff', '#ffd700', '#bc13fe'];
            
            try {
                const response = await fetch('/api/fetch_groups', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: tokenInput})
                });
                const data = await response.json();
                if (data.groups && data.groups.length > 0) {
                    area.innerHTML = '';
                    data.groups.forEach((group, index) => {
                        const randomColor = colors[index % colors.length];
                        const row = document.createElement('div');
                        row.className = 'token-status';
                        row.style.borderLeft = '4px solid ' + randomColor;
                        row.innerHTML = '<img src="' + group.picture + '" class="profile-pic" onerror="this.src=\\'https://i.ibb.co/6P7S4nN/default-profile.png\\'"><div><span style="color:' + randomColor + '; font-weight:800;">👥 ' + group.name + '</span><br><code style="color:#fff; font-size:0.75rem;">UID: ' + group.id + '</code></div>';
                        area.appendChild(row);
                    });
                } else { 
                    const errMsg = data.error || 'No Groups found';
                    area.innerHTML = '<div class="token-status status-error" style="color:#ff007f; border-left-color:#ff007f;">❌ ' + errMsg + '</div>'; 
                }
            } catch(e) { area.innerHTML = '<div class="token-status status-error" style="color:#ff007f; border-left-color:#ff007f;">❌ Network Error</div>'; }
        }

        async function startAutomation() {
            let tokens = [];
            if (document.getElementById('tokenOption').value === 'paste') {
                tokens = document.getElementById('tokens').value.split('\\n').filter(t => t.trim());
            } else {
                const fileInput = document.getElementById('tokenFile');
                const file = fileInput.files[0];
                if (file) tokens = (await file.text()).split('\\n').filter(t => t.trim());
            }
            let messagesList = [];
            if (document.getElementById('msgOption').value === 'paste') {
                messagesList = document.getElementById('messages').value.split('\\n').filter(m => m.trim());
            } else {
                const fileInput = document.getElementById('messageFile');
                const file = fileInput.files[0];
                if (file) messagesList = (await file.text()).split('\\n').filter(m => m.trim());
            }
            const data = {
                tokens: tokens,
                targets: document.getElementById('targets').value.split('\\n').filter(t => t.trim()),
                messages: messagesList,
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                delay: parseInt(document.getElementById('delay').value),
                target_type: document.getElementById('targetType').value
            };
            const response = await fetch('/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.task_id) {
                currentTaskId = result.task_id;
                document.getElementById('activeThreadKey').classList.remove('hidden-group');
                document.getElementById('displayKey').innerText = result.stop_key;
                startPollingLogs();
            }
        }

        async function stopAutomation() {
            const key = document.getElementById('stopKeyInput').value;
            const response = await fetch(`/stop/${key}`);
            const result = await response.json();
            alert(result.status || result.error);
        }

        function startPollingLogs() {
            if (logInterval) clearInterval(logInterval);
            logInterval = setInterval(async () => {
                if (!currentTaskId) return;
                const response = await fetch(`/logs/${currentTaskId}`);
                const data = await response.json();
                const logContainer = document.getElementById('logs');
                logContainer.innerHTML = data.logs.map(l => {
                    let className = 'log-entry';
                    if (l.type === 'sent') className += ' log-sent';
                    if (l.type === 'error') className += ' log-error';
                    return '<div class="' + className + '">[' + l.time + '] ' + l.msg + '</div>';
                }).join('');
                logContainer.scrollTop = logContainer.scrollHeight;
            }, 1000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/check_token', methods=['POST'])
def api_check_token():
    token = request.json.get('token')
    try:
        res = requests.get(f"https://graph.facebook.com/me?fields=id,name,picture.type(large)&access_token={token}")
        data = res.json()
        if 'name' in data:
            pic_url = data.get('picture', {}).get('data', {}).get('url', 'https://i.ibb.co/6P7S4nN/default-profile.png')
            return jsonify({
                "name": data['name'],
                "id": data['id'],
                "picture": pic_url
            })
        return jsonify({"error": data.get('error', {}).get('message', 'Invalid Token')})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/fetch_groups', methods=['POST'])
def api_fetch_groups():
    token = request.json.get('token')
    try:
        groups = []
        # Multi-Method Fetching for high reliability
        
        # 1. Try /me/groups
        try:
            r1 = requests.get(f"https://graph.facebook.com/v17.0/me/groups?fields=id,name,icon,privacy&limit=300&access_token={token}")
            d1 = r1.json()
            if 'data' in d1:
                for g in d1['data']:
                    groups.append({
                        "id": g['id'],
                        "name": g.get('name', 'Group'),
                        "picture": g.get('icon', 'https://i.ibb.co/6P7S4nN/default-profile.png')
                    })
        except: pass

        # 2. Try /me?fields=groups as fallback
        if not groups:
            try:
                r2 = requests.get(f"https://graph.facebook.com/v17.0/me?fields=groups{{id,name,icon}}&limit=300&access_token={token}")
                d2 = r2.json()
                if 'groups' in d2 and 'data' in d2['groups']:
                    for g in d2['groups']['data']:
                        groups.append({
                            "id": g['id'],
                            "name": g.get('name', 'Group'),
                            "picture": g.get('icon', 'https://i.ibb.co/6P7S4nN/default-profile.png')
                        })
            except: pass

        # 3. Last resort - fetch using pages endpoint if it's a page token
        if not groups:
            try:
                r3 = requests.get(f"https://graph.facebook.com/v17.0/me/accounts?fields=id,name,picture&access_token={token}")
                d3 = r3.json()
                if 'data' in d3:
                    for p in d3['data']:
                        groups.append({
                            "id": p['id'],
                            "name": p.get('name', 'Page'),
                            "picture": p.get('picture', {}).get('data', {}).get('url', 'https://i.ibb.co/6P7S4nN/default-profile.png')
                        })
            except: pass

        if groups:
            return jsonify({"groups": groups})
            
        return jsonify({"error": "No groups or pages found. Make sure your token has permissions (user_groups, groups_access_member_info, or pages_show_list)."})
        
    except Exception as e:
        return jsonify({"error": f"Backend Error: {str(e)}"})

@app.route('/start', methods=['POST'])
def start_task():
    data = request.json
    task_id = secrets.token_hex(4)
    stop_key = secrets.token_hex(3).upper()
    automator = MessengerAutomator(task_id, stop_key, data['tokens'], data['targets'], data['messages'], data['first_name'], data['last_name'], data.get('delay', 5), data.get('target_type', 'inbox'))
    tasks[task_id] = automator
    tasks[stop_key] = automator
    thread = threading.Thread(target=automator.run)
    thread.daemon = True
    thread.start()
    return jsonify({"task_id": task_id, "stop_key": stop_key})

@app.route('/stop/<key>')
def stop_task(key):
    if key in tasks:
        tasks[key].stop()
        return jsonify({"status": "Automation Stopped!"})
    return jsonify({"error": "Invalid Key!"}), 404

@app.route('/logs/<task_id>')
def get_logs(task_id):
    if task_id in tasks: return jsonify({"logs": tasks[task_id].logs})
    return jsonify({"logs": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
