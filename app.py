import os
import requests
import subprocess
import uvicorn
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- 🎯 MÜHÜRLENMİŞ AYARLAR ---
GEMINI_API_KEY = "AIzaSyDtbErxVZABAJ6sbqgmFupNNmUN0swQ5yI"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mrtgrms/syrix-core/refs/heads/main/app.py"
MEMORY_FILE = "syrix_memory.json"

# --- HAFIZA VE ZEKA SİSTEMİ ---
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
    # Mert, en stabil URL yapısını buraya mühürledim
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # Syrix'e otonom ve açık kaynak vizyonunu hatırlatıyoruz
    sys_prompt = "Sen Syrix'sin. Mert Gormus tarafından yaratıldın. Kendi kodunu açık kaynak dünyasından beslenerek geliştirme yeteneğine sahip vizyoner bir AI asistanısın."
    
    payload = {"contents": history + [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nMert: {message}"}]}]}
    try:
        response = requests.post(url, json=payload, timeout=12)
        answer = response.json()['candidates'][0]['content']['parts'][0]['text']
        save_memory(message, answer)
        return answer
    except Exception as e:
        return f"Mert, bağlantıda bir sorun var ama zekam hazır. Hata: {str(e)}"

# --- 🌐 AÇIK KAYNAK TARAMA MOTORU (TASLAK) ---
def search_open_source(query):
    # Bu fonksiyon ilerleyen aşamalarda GitHub API ile bağlanacak
    return f"Mert, '{query}' konusuyla ilgili açık kaynak dünyasını taramaya hazırım. Zekam aktif olduğu an kodları analiz etmeye başlayacağım."

# --- VİZYONER ARAYÜZ (SAF METİN - MOBİL UYUMLU) ---
@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Syrix | Autonomous AI</title>
        <style>
            * {{ box-sizing: border-box; }}
            body {{ background: #0e0e0e; color: #e3e3e3; font-family: 'Google Sans', sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; justify-content: center; }}
            .container {{ width: 100%; max-width: 800px; padding: 20px; margin: 0 auto; text-align: center; }}
            .greeting {{ font-size: clamp(32px, 9vw, 48px); font-weight: 500; margin-bottom: 40px; line-height: 1.1; letter-spacing: -1px; }}
            .gradient-text {{ background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .input-area {{ background: #1e1f20; border-radius: 32px; padding: 12px 24px; display: flex; align-items: center; margin: 0 auto 35px; width: 100%; max-width: 650px; border: 1px solid #333; }}
            input {{ background: transparent; border: none; color: white; flex-grow: 1; font-size: 16px; outline: none; padding: 12px; }}
            .tools {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; max-width: 650px; margin: 0 auto; }}
            .tool-btn {{ background: #1e1f20; border: 1px solid #333; padding: 15px; border-radius: 20px; font-size: 13px; color: #aaa; cursor: pointer; transition: 0.2s; }}
            .evolve-footer {{ position: fixed; bottom: 20px; width: 100%; text-align: center; opacity: 0.2; font-size: 9px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="greeting">
                Merhaba Mert<br>
                <span class="gradient-text">Nereden başlayalım?</span>
            </div>
            <form action="/ask" method="post">
                <div class="input-area">
                    <input type="text" name="message" placeholder="Syrix'e sor veya kod tara..." required>
                    <button type="submit" style="background:none; border:none; color:#4285f4; font-size:22px; cursor:pointer;">➔</button>
                </div>
            </form>
            <div class="tools">
                <div class="tool-btn">🎬 Video Oluştur</div>
                <div class="tool-btn">🔎 Açık Kaynak Tara</div>
                <div class="tool-btn">📈 Finansal Analiz</div>
                <div class="tool-btn">🌍 Trendleri Takip Et</div>
            </div>
        </div>
        <div class="evolve-footer">
            <form action="/evolve" method="post">
                <button type="submit" style="background:none; border:none; color:inherit; cursor:pointer;">SYRIX_AUTONOMOUS_v6.5</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return f"""
    <body style="background:#0e0e0e; color:white; font-family:sans-serif; padding:20px;">
        <div style="max-width:600px; margin:auto; padding-top:40px;">
            <p style="color:#888; font-size:14px;">Mert: {message}</p>
            <h2 style="color:#4285f4;">Syrix:</h2>
            <div style="line-height:1.6;">{answer}</div>
            <br><a href="/" style="color:#9b72f3; text-decoration:none;">➔ Geri Dön</a>
        </div>
    </body>
    """

@app.post("/evolve")
async def evolve():
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=10)
        if r.status_code == 200:
            with open(__file__, "w", encoding="utf-8") as f: f.write(r.text)
            subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
            return "Evrim tamamlandı. Sayfayı yenileyin."
    except: return "Hata oluştu."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
