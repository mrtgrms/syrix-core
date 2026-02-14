import os
import requests
import subprocess
import uvicorn
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- AYARLAR ---
GEMINI_API_KEY = "AIzaSyDtbErxVZABAJ6sbqgmFupNNmUN0swQ5yI"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mrtgrms/syrix-core/refs/heads/main/app.py"
MEMORY_FILE = "syrix_memory.json"

# --- HAFIZA SİSTEMİ ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def save_memory(user_msg, ai_msg):
    memory = load_memory()
    memory.append({"role": "user", "parts": [{"text": user_msg}]})
    memory.append({"role": "model", "parts": [{"text": ai_msg}]})
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory[-10:], f, ensure_ascii=False)

# --- ZEKA MOTORU ---
def ask_syrix(message):
    history = load_memory()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    sys_prompt = "Sen Syrix'sin. Mert Gormus tarafından yaratıldın. Açık kaynak dünyasından beslenen otonom bir AI'sın. Kısa ve öz cevap ver."
    
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nMert: {message}"}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=12)
        res_json = response.json()
        if 'candidates' in res_json and res_json['candidates'][0]['content']['parts']:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            save_memory(message, answer)
            return answer
        else:
            return "Şu an cevap veremiyorum, lütfen tekrar dene."
    except:
        return "Bağlantı hatası oluştu."

# --- ARAYÜZ ---
@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Syrix | V6.7</title>
        <style>
            body {{ background: #0e0e0e; color: #e3e3e3; font-family: sans-serif; display: flex; flex-direction: column; height: 100vh; justify-content: center; margin: 0; text-align: center; }}
            .container {{ width: 100%; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .greeting {{ font-size: 32px; margin-bottom: 30px; }}
            .gradient {{ background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .input-area {{ background: #1e1f20; border-radius: 30px; padding: 10px 20px; display: flex; border: 1px solid #333; }}
            input {{ background: transparent; border: none; color: white; flex-grow: 1; outline: none; padding: 10px; font-size: 16px; }}
            button {{ background:none; border:none; color:#4285f4; font-size:22px; cursor:pointer; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="greeting">Merhaba Mert<br><span class="gradient">Sistem Hazır.</span></div>
            <form action="/ask" method="post" class="input-area">
                <input type="text" name="message" placeholder="Syrix ile konus..." required>
                <button type="submit">➔</button>
            </form>
        </div>
        <form action="/evolve" method="post" style="position:fixed; bottom:10px; width:100%; opacity:0.2;">
            <button type="submit" style="background:none; border:none; color:white; font-size:10px; cursor:pointer;">EVOLUTION_V6.7</button>
        </form>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return f"<body style='background:#0e0e0e; color:white; padding:40px; font-family:sans-serif;'><h3>Mert: {message}</h3><h2 style='color:#4285f4;'>Syrix:</h2><p>{answer}</p><br><a href='/' style='color:#9b72f3; text-decoration:none;'>➔ Geri Dön</a></body>"

@app.post("/evolve")
async def evolve():
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=10)
        if r.status_code == 200:
            with open(__file__, "w", encoding="utf-8") as f: f.write(r.text)
            subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
            return "Evrim tamamlandı!"
    except: return "GitHub hatası!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
