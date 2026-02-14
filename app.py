import os
import requests
import datetime
import random
import subprocess
import uvicorn
import json
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# --- 🎯 BURAYI KENDİ BİLGİLERİNLE DOLDUR ---
GEMINI_API_KEY = "AIzaSyBFcJJAVE6Qhwor8eTnEcPXPgylMwunOjI"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mrtgrms/syrix-core/refs/heads/main/app.py"

# --- DİĞER AYARLAR ---
HF_MOTOR_URL = "https://syrix-ai-syrix-core.hf.space/create"
MEMORY_FILE = "syrix_memory.json"

# --- HAFIZA SİSTEMİ (Mert'i Unutmaması İçin) ---
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
        json.dump(memory[-20:], f, ensure_ascii=False, indent=2)

# --- ZEKA MOTORU (Gemini 1.5 Flash) ---
def ask_syrix(message):
    history = load_memory()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    system_instruction = "Sen Syrix'sin. Mert Gormus tarafından yaratılan, Horizon Origin imparatorluğunu yöneten akıllı bir asistansın. Mert ile samimi ve zeki bir ortak gibi konuş."
    
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"{system_instruction}\n\nMert: {message}"}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        ai_response = response.json()['candidates'][0]['content']['parts'][0]['text']
        save_memory(message, ai_response)
        return ai_response
    except:
        return "Mert, şu an zihnimi toparlayamadım. API anahtarını kontrol eder misin?"

# --- EVRİM MOTORU (Gelişim Sistemi) ---
def evolve_syrix():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=15)
        if response.status_code == 200:
            new_code = response.text
            with open(__file__, "w", encoding="utf-8") as f:
                f.write(new_code)
            subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
            return True
        return False
    except: return False

# --- VİZYONER ARAYÜZ ---
@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Syrix AI v5.5 | Smart Director</title>
        <style>
            body {{ font-family: sans-serif; margin: 0; background: #050505; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
            .card {{ background: rgba(20, 20, 20, 0.9); padding: 40px; border-radius: 40px; border: 1px solid #333; width: 400px; text-align: center; }}
            h1 {{ background: linear-gradient(90deg, #4285F4, #a158ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .input-group {{ background: #111; border-radius: 20px; padding: 10px; display: flex; border: 1px solid #222; margin-top: 20px; }}
            input {{ background: transparent; border: none; color: white; outline: none; flex-grow: 1; padding: 10px; }}
            button {{ background: #4285F4; color: white; border: none; padding: 10px 20px; border-radius: 15px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Syrix AI</h1>
            <p style="color: #666;">Yönetmen Koltuğu: Mert</p>
            
            <div style="text-align: left; margin-top: 20px;">
                <p style="font-size: 12px; color: #a158ff;">🧠 ZEKA & SOHBET</p>
                <form action="/ask" method="post" class="input-group">
                    <input type="text" name="message" placeholder="Bana bir şey sor Mert..." required>
                    <button type="submit">💬</button>
                </form>
            </div>

            <form action="/evolve" method="post">
                <button type="submit" style="background: none; border: 1px solid #333; color: #555; margin-top: 30px; width: 100%; padding: 10px; border-radius: 10px; cursor: pointer;">⚙️ GELİŞİMİ TETİKLE</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return f"""
    <body style="background:#050505; color:white; padding:50px; font-family:sans-serif;">
        <div style="max-width:500px; margin:auto; background:#111; padding:30px; border-radius:30px; border:1px solid #333;">
            <h3 style="color:#a158ff;">Syrix:</h3>
            <p>{answer}</p>
            <br>
            <a href="/" style="color:#4285F4; text-decoration:none;">➔ Geri Dön</a>
        </div>
    </body>
    """

@app.post("/evolve")
async def manual_evolve():
    success = evolve_syrix()
    msg = "🧬 Yenileniyorum Mert..." if success else "⚠️ Zaten güncelim."
    return f"<body style='background:#050505; color:white; text-align:center; padding-top:100px;'><h2>{msg}</h2><a href='/'>Dön</a></body>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
