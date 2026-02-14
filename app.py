import os
import requests
import subprocess
import uvicorn
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- 🎯 AYARLAR ---
GEMINI_API_KEY = "AIzaSyDtbErxVZABAJ6sbqgmFupNNmUN0swQ5yI"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mrtgrms/syrix-core/refs/heads/main/app.py"
MEMORY_FILE = "syrix_memory.json"

# --- HAFIZA VE ZEKA MOTORU ---
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

def ask_syrix(message):
    history = load_memory()
    # HATA ÇÖZÜMÜ: Model ismini kesin formatta güncelledim
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-001:generateContent?key={GEMINI_API_KEY}"
    sys_prompt = "Sen Syrix'sin. Mert Gormus'un asistanısın. Gemini tarzında, şık ve vizyoner cevaplar ver."
    
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nMert: {message}"}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=12)
        res_json = response.json()
        if 'candidates' in res_json:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            save_memory(message, answer)
            return answer
        return f"Zekada bir sorun oluştu: {res_json.get('error', {}).get('message', 'Bağlantı kesildi')}"
    except:
        return "Bağlantı kurulamadı."

# --- 🎨 TEK SAYFA GEMINI ARAYÜZÜ ---
@app.get("/", response_class=HTMLResponse)
async def index(msg: str = None, ans: str = None):
    chat_html = ""
    if msg and ans:
        chat_html = f"""
        <div style="margin-top:40px; text-align:left; max-width:700px; margin-left:auto; margin-right:auto;">
            <p style="color:#888; font-size:14px;">Mert: {msg}</p>
            <div style="color:#e3e3e3; font-size:16px; line-height:1.6; background:#1e1f20; padding:20px; border-radius:20px; border-left:4px solid #4285f4;">
                <span style="color:#4285f4; font-size:20px;">✦</span> {ans}
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gemini | Syrix</title>
        <style>
            body {{ background: #131314; color: #e3e3e3; font-family: 'Google Sans', sans-serif; margin: 0; padding: 20px; }}
            .main-container {{ max-width: 800px; margin: 100px auto; text-align: center; }}
            .greeting {{ font-size: clamp(32px, 7vw, 52px); font-weight: 500; margin-bottom: 40px; }}
            .gradient-text {{ background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            
            .chat-container {{ background: #1e1f20; border-radius: 32px; padding: 10px 24px; display: flex; align-items: center; max-width: 700px; margin: 0 auto; border: 1px solid #333; }}
            input {{ background: transparent; border: none; color: white; flex-grow: 1; font-size: 16px; outline: none; padding: 15px; }}
            button {{ background:none; border:none; color:#4285f4; font-size:24px; cursor:pointer; }}
            
            .tools {{ display: flex; gap: 10px; justify-content: center; margin-top: 25px; flex-wrap: wrap; }}
            .tool-btn {{ background: #1e1f20; border: 1px solid #333; padding: 10px 18px; border-radius: 20px; font-size: 13px; color: #aaa; cursor: pointer; transition: 0.2s; }}
            .tool-btn:hover {{ background: #333; }}
            
            .footer {{ position: fixed; bottom: 15px; width: 100%; left: 0; text-align: center; opacity: 0.2; font-size: 10px; }}
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="greeting">
                Merhaba Mert<br>
                <span class="gradient-text">Nereden başlayalım?</span>
            </div>
            
            <form action="/ask" method="post" class="chat-container">
                <input type="text" name="message" placeholder="Gemini'ye sorun" required autocomplete="off">
                <button type="submit">➔</button>
            </form>

            <div class="tools">
                <div class="tool-btn">✨ Resim Oluştur</div>
                <div class="tool-btn">🎬 Video oluşturun</div>
                <div class="tool-btn">💡 Ne istiyorsanız yazın</div>
            </div>

            {chat_html}
        </div>

        <form action="/evolve" method="post" class="footer">
            <button type="submit" style="background:none; border:none; color:inherit; font-size:inherit; cursor:pointer;">SYRIX_PURE_GEMINI_v6.9</button>
        </form>
    </body>
    </html>
    """

@app.post("/ask")
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return await index(msg=message, ans=answer)

@app.post("/evolve")
async def evolve():
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=10)
        if r.status_code == 200:
            with open(__file__, "w", encoding="utf-8") as f: f.write(r.text)
            subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
            return "Sistem Evrimleşti."
    except: return "GitHub Hatası."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
