import os
import requests
import random
import subprocess
import uvicorn
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- AYARLAR ---
GEMINI_API_KEY = "AIzaSyDvCukyIggrjeOILVTPiEUmc0O8VBdjfP8"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mrtgrms/syrix-core/refs/heads/main/app.py"
MEMORY_FILE = "syrix_memory.json"

# --- KORUNAN ÖZELLİKLER (ZEKA & HAFIZA) ---
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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    sys_prompt = "Sen Syrix'sin. Mert Gormus'un otonom asistanısın. Kısa, zeki ve vizyoner cevaplar ver."
    payload = {"contents": history + [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nMert: {message}"}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        answer = response.json()['candidates'][0]['content']['parts'][0]['text']
        save_memory(message, answer)
        return answer
    except: return "Mert, API bağlantısı kurulamadı."

# --- ARAYÜZ (GEMINI STYLE) ---
@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Syrix | Gemini Vision</title>
        <style>
            body {{ background: #0e0e0e; color: #e3e3e3; font-family: 'Google Sans', sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            .container {{ text-align: center; width: 100%; max-width: 800px; padding: 20px; }}
            .greeting {{ font-size: 40px; font-weight: 500; margin-bottom: 40px; }}
            .gradient-text {{ background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            
            .input-area {{ background: #1e1f20; border-radius: 32px; padding: 15px 25px; display: flex; align-items: center; margin-bottom: 25px; transition: 0.3s; }}
            .input-area:focus-within {{ background: #28292a; box-shadow: 0 1px 10px rgba(0,0,0,0.5); }}
            input {{ background: transparent; border: none; color: white; flex-grow: 1; font-size: 16px; outline: none; padding: 10px; }}
            
            .tools {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
            .tool-btn {{ background: #1e1f20; border: 1px solid #333; padding: 10px 20px; border-radius: 20px; font-size: 13px; color: #aaa; cursor: pointer; transition: 0.3s; }}
            .tool-btn:hover {{ background: #333; color: white; }}
            
            .evolve-trigger {{ position: absolute; bottom: 20px; opacity: 0.3; font-size: 10px; cursor: pointer; }}
            .evolve-trigger:hover {{ opacity: 1; color: #4285f4; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="greeting">
                <span style="color: #4285f4;">✦</span> Merhaba Mert<br>
                <span class="gradient-text">Nereden başlayalım?</span>
            </div>
            
            <form action="/ask" method="post" class="input-group">
                <div class="input-area">
                    <input type="text" name="message" placeholder="Syrix'e bir şeyler sor veya komut ver..." required>
                    <button type="submit" style="background:none; border:none; color:#4285f4; font-size:20px; cursor:pointer;">➔</button>
                </div>
            </form>

            <div class="tools">
                <div class="tool-btn" onclick="location.href='/action/video'">🎬 Video Oluştur</div>
                <div class="tool-btn" onclick="location.href='/action/gizem'">🔎 Gizem Bul</div>
                <div class="tool-btn" onclick="location.href='/action/finans'">📈 Finansal Analiz</div>
                <div class="tool-btn" onclick="location.href='/action/trend'">🌍 Trendleri Tara</div>
            </div>
        </div>

        <form action="/evolve" method="post" class="evolve-trigger">
            <button type="submit" style="background:none; border:none; color:inherit; cursor:pointer;">SYSTEM_EVOLUTION_v6.0</button>
        </form>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return f"""
    <body style="background:#0e0e0e; color:white; font-family:sans-serif; padding:50px;">
        <div style="max-width:700px; margin:auto; line-height:1.6;">
            <p style="color:#888;">Mert: {message}</p>
            <h2 style="color:#4285f4;">Syrix:</h2>
            <p>{answer}</p>
            <br>
            <a href="/" style="color:#9b72f3; text-decoration:none;">➔ Yeni bir soru sor</a>
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
            return "Sistem evrimleşti."
    except: return "Hata oluştu."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
