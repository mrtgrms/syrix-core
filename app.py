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
    # EN STABİL MODEL: 'gemini-1.5-flash' (Hata almamak için en geniş uyumlu versiyon)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    sys_prompt = "Sen Syrix'sin. Mert Gormus'un asistanısın. Horizon Origin ve otonom sistemler hakkında bilgilisin. Gemini gibi şık cevap ver."
    
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
        return f"Google Hatası: {res_json.get('error', {}).get('message', 'Model baglantisi koptu.')}"
    except:
        return "Sunucuya ulasilamiyor."

# --- 🎨 TAM GEMINI TASARIMI ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, msg: str = None, ans: str = None):
    chat_bubble = ""
    if msg and ans:
        chat_bubble = f"""
        <div style="width:100%; max-width:700px; margin: 40px auto; text-align: left;">
            <div style="background: #2b2c2f; padding: 12px 20px; border-radius: 20px; display: inline-block; float: right; color: white; margin-bottom: 20px;">
                {msg}
            </div>
            <div style="clear: both;"></div>
            <div style="display: flex; gap: 15px; align-items: flex-start; margin-bottom: 30px;">
                <div style="color: #4285f4; font-size: 24px;">✦</div>
                <div style="color: #e3e3e3; line-height: 1.6; font-size: 16px; white-space: pre-wrap;">{ans}</div>
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
            body {{ background: #131314; color: #e3e3e3; font-family: 'Google Sans', sans-serif; margin: 0; display: flex; flex-direction: column; min-height: 100vh; }}
            .content {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }}
            .greeting {{ font-size: clamp(30px, 6vw, 56px); font-weight: 500; margin-bottom: 40px; text-align: center; }}
            .gradient {{ background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            
            .input-box {{ background: #1e1f20; border-radius: 32px; padding: 10px 24px; display: flex; align-items: center; width: 100%; max-width: 700px; transition: 0.2s; }}
            input {{ background: transparent; border: none; color: white; flex-grow: 1; font-size: 16px; outline: none; padding: 15px; }}
            
            .tools {{ display: flex; gap: 10px; margin-top: 25px; flex-wrap: wrap; justify-content: center; }}
            .tool {{ background: #1e1f20; border: 1px solid #333; padding: 12px 20px; border-radius: 20px; font-size: 13px; color: #aaa; cursor: pointer; }}
            .tool:hover {{ background: #333; color: white; }}
        </style>
    </head>
    <body>
        <div class="content">
            {f'<div class="greeting">Merhaba Mert,<br><span class="gradient">Nereden başlayalım?</span></div>' if not msg else ''}
            
            {chat_bubble}

            <form action="/ask" method="post" style="width: 100%; display: flex; justify-content: center; margin-top: 20px;">
                <div class="input-box">
                    <input type="text" name="message" placeholder="Gemini 3'e sorun" required autocomplete="off">
                    <button type="submit" style="background:none; border:none; color:#4285f4; font-size:24px; cursor:pointer;">➔</button>
                </div>
            </form>

            <div class="tools">
                <div class="tool">✨ Resim Oluştur</div>
                <div class="tool">🎬 Video oluşturun</div>
                <div class="tool">💡 Proje Analizi</div>
            </div>
        </div>
        
        <form action="/evolve" method="post" style="padding: 20px; text-align: center; opacity: 0.2;">
            <button type="submit" style="background:none; border:none; color:white; font-size:10px; cursor:pointer;">SYRIX_PRO_v7.0</button>
        </form>
    </body>
    </html>
    """

@app.post("/ask", response_class=HTMLResponse)
async def ask(message: str = Form(...)):
    answer = ask_syrix(message)
    return await index(Request, msg=message, ans=answer)

@app.post("/evolve")
async def evolve():
    try:
        r = requests.get(GITHUB_RAW_URL, timeout=10)
        if r.status_code == 200:
            with open(__file__, "w", encoding="utf-8") as f: f.write(r.text)
            subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
            return "Sistem Guncellendi."
    except: return "Baglanti Hatasi."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
