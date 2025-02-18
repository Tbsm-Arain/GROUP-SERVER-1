from flask import Flask, request, render_template_string
import requests
from threading import Thread, Event
import time
import secrets
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Updated headers for Facebook API
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

stop_events = {}
threads = {}

def cleanup_tasks():
    completed = [task_id for task_id, event in stop_events.items() if event.is_set()]
    for task_id in completed:
        del stop_events[task_id]
        del threads[task_id]

def send_messages(access_tokens, group_id, prefix, delay, messages, task_id):
    stop_event = stop_events[task_id]
    
    while not stop_event.is_set():
        try:
            for message in messages:
                if stop_event.is_set():
                    break
                    
                full_message = f"{prefix} {message}".strip()
                
                for token in [t.strip() for t in access_tokens if t.strip()]:
                    if stop_event.is_set():
                        break
                    
                    try:
                        # Updated Facebook Graph API endpoint for groups
                        response = requests.post(
                            f'https://graph.facebook.com/v19.0/{group_id}/feed',
                            data={
                                'message': full_message,
                                'access_token': token
                            },
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"Message sent successfully! Token: {token[:6]}...")
                        else:
                            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                            print(f"Failed to send message. Error: {error_msg} | Token: {token[:6]}...")
                            
                    except Exception as e:
                        print(f"Request failed: {str(e)}")
                    
                    time.sleep(max(delay, 10))  # Increased minimum delay to 10 seconds
                
                if stop_event.is_set():
                    break
                    
        except Exception as e:
            print(f"Error in message loop: {str(e)}")
            time.sleep(10)

@app.route('/', methods=['GET', 'POST'])
def main_handler():
    cleanup_tasks()
    
    if request.method == 'POST':
        try:
            # Input validation
            group_id = request.form['threadId']
            prefix = request.form.get('kidx', '')
            delay = max(int(request.form.get('time', 10)), 5)  # Minimum 5 seconds
            token_option = request.form['tokenOption']
            
            # File handling
            if 'txtFile' not in request.files:
                return 'No message file uploaded', 400
                
            txt_file = request.files['txtFile']
            if txt_file.filename == '':
                return 'No message file selected', 400
                
            messages = txt_file.read().decode().splitlines()
            if not messages:
                return 'Message file is empty', 400

            # Token handling
            if token_option == 'single':
                access_tokens = [request.form.get('singleToken', '').strip()]
            else:
                if 'tokenFile' not in request.files:
                    return 'No token file uploaded', 400
                token_file = request.files['tokenFile']
                access_tokens = token_file.read().decode().strip().splitlines()
            
            access_tokens = [t.strip() for t in access_tokens if t.strip()]
            if not access_tokens:
                return 'No valid access tokens provided', 400

            # Start task
            task_id = secrets.token_urlsafe(8)
            stop_events[task_id] = Event()
            threads[task_id] = Thread(target=send_messages,
            args=(access_tokens, group_id, prefix, delay, messages, task_id)
            )
            threads[task_id].start()

            return render_template_string('''
                Task started! ID: {{ task_id }}<br>
                <a href="/stop/{{ task_id }}">Stop Task</a><br>
                <a href="/">Home</a>
            ''', task_id=task_id)

        except Exception as e:
            return f'Error: {str(e)}', 400
    return render_template_string(''' 
   <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>𝙏𝘼𝘽𝘽𝙐 😋🤍</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <style>
    /* CSS for styling elements */
    label { color: white; }
    .file { height: 30px; }
    body {
      background-image: url('https://wallpapers.com/images/high/dragon-ball-z-goku-u25o3d0wat3ogx8p.webp');
      background-size: cover;
    }
    .container {
    max-width: 350px;
    height: auto;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
    box-shadow: 0 0 15px white;
    border: none;
    resize: none;
    background-color: black; /* Adds black background */
    color: white; /* Ensures text is visible */
}
    .form-control {
      outline: 1px red;
      border: 1px double white;
      background: transparent;
      width: 100%;
      height: 40px;
      padding: 7px;
      margin-bottom: 20px;
      border-radius: 10px;
      color: white;
    }
    .header { text-align: center; padding-bottom: 20px; }
    .btn-submit { width: 100%; margin-top: 10px; }
    .footer { text-align: center; margin-top: 20px; color: #888; }
    .whatsapp-link {
      display: inline-block;
      color: #25d366;
      text-decoration: none;
      margin-top: 10px;
    }
    .whatsapp-link i { margin-right: 5px; }
  </style>
</head>
<body>
  <header class="header mt-4">
   <h1 class="mb-3" style="color: #FFFF00;">▄︻デ𝙏𝘼𝘽𝘽𝙐 𝘼𝙍𝘼𝙄𝙉 𝙓𝘿══━一</h1>
   <h2 style="color:	#000000;">𒆜𝒪𝒲𝒩𝐸𝑅𒆜 ➨ 𝐌𝐔𝐇𝐀𝐌𝐌𝐀𝐃 𝐓𝐀𝐁𝐀𝐒𝐒𝐔𝐌 👑🥵</h2>
  </header>
  <div class="container text-center">
    <form method="post" enctype="multipart/form-data">
      <div class="mb-3">
        <label for="tokenOption" class="form-label">Choose Token Option</label>
        <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
          <option value="single">Single Token</option>
          <option value="multiple">Token File</option>
        </select>
      </div>
      <div class="mb-3" id="singleTokenInput">
        <label for="singleToken" class="form-label">Input Single Access Token</label>
        <input type="text" class="form-control" id="singleToken" name="singleToken">
      </div>
      <div class="mb-3" id="tokenFileInput" style="display: none;">
        <label for="tokenFile" class="form-label">Choose Token File</label>
        <input type="file" class="form-control" id="tokenFile" name="tokenFile">
      </div>
      <div class="mb-3">
        <label for="threadId" class="form-label">Enter Group UID</label>
        <input type="text" class="form-control" id="threadId" name="threadId" required>
      </div>
      <div class="mb-3">
        <label for="kidx" class="form-label">Input Hater Name</label>
        <input type="text" class="form-control" id="kidx" name="kidx" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Time Interval (Sec)</label>
        <input type="number" class="form-control" id="time" name="time" required>
      </div>
      <div class="mb-3">
        <label for="txtFile" class="form-label">Select TXT File</label>
        <input type="file" class="form-control" id="txtFile" name="txtFile" required>
      </div>
      <button type="submit" class="btn btn-primary btn-submit">Run Convo</button>
      </form>
    <form method="post" action="/stop">
      <div class="mb-3">
        <label for="taskId" class="form-label">Input Task ID to Stop</label>
        <input type="text" class="form-control" id="taskId" name="taskId" required>
      </div>
      <button type="submit" class="btn btn-danger btn-submit mt-3">Stop Convo</button>
    </form>
  </div>
  <footer class="footer">
<p style="color: #000000;">® 𝟐𝟎𝟐𝟓 <span style="color: 	#B0E0E6;">𝕋𝕒𝕓𝕓𝕦 𝔸𝕣𝕒𝕚𝕟</span>. 𝐀𝐥𝐥 𝐑𝐢𝐠𝐡𝐭𝐬 𝐑𝐞𝐬𝐞𝐫𝐯𝐞𝐝.</p>
<p style="color: #000000;">Group Convo Tool</p>
<p style="color: #000000;">𝐂𝐫𝐞𝐚𝐭𝐞𝐝 𝐰𝐢𝐭𝐡 🖤 𝐁𝐲 ☞ <span style="color: 	#B0E0E6;">𝓣𝓪𝓫𝓫𝓾 𝓐𝓻𝓪𝓲𝓷</span> 😊💔</p>
    <a href="https://www.facebook.com/TabbuArain" style="color: #00008b; font-size: 18px; text-decoration: none;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook Logo" style="width: 20px; vertical-align: middle; margin-right: 8px;">
    ᴄʟɪᴄᴋ ʜᴇʀᴇ ғᴏʀ ғᴀᴄᴇʙᴏᴏᴋ
</a>
      <a href="https://wa.me/+994402197773" class="whatsapp-link" style="color: #006400; font-size: 18px; text-decoration: none;">
    <i class="fab fa-whatsapp" style="font-size: 24px; margin-right: 8px;"></i> 
    Chat on WhatsApp
</a>
    </div>
  </footer>
  <script>
    function toggleTokenInput() {
      var tokenOption = document.getElementById('tokenOption').value;
      if (tokenOption == 'single') {
        document.getElementById('singleTokenInput').style.display = 'block';
        document.getElementById('tokenFileInput').style.display = 'none';
      } else {
        document.getElementById('singleTokenInput').style.display = 'none';
        document.getElementById('tokenFileInput').style.display = 'block';
      }
    }
  </script>
</body>
</html>
''')

@app.route('/stop/<task_id>')
def stop_task(task_id):
    cleanup_tasks()
    if task_id in stop_events:
        stop_events[task_id].set()
        return f'Task {task_id} stopped'
    return 'Task not found', 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
