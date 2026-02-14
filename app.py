import os
import requests
import datetime
import random
import subprocess
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()

# --- AYARLAR ---
HF_MOTOR_URL = "https://syrix-ai-syrix-core.hf.space/create"
# Mert, GitHub repo linkini oluşturduktan sonra burayı güncellemelisin.
GITHUB_RAW_URL = "https://raw.githubusercontent.com/mertgormus27/syrix/main/app.py"

def get_director_advice():
    advices = [
        "Mert, bugün Amerika'da 'Gizli Dosyalar' trendi yükselişte. Yeni bir gizem patlatalım!",
        "Horizon Origin bugün dünden daha güçlü. Hadi yeni bir başyapıt üretelim!",
        "Sistemi GitHub üzerinden sürekli tarıyorum, en ufak bir iyileştirmeyi anında kapacağım.",
        "Mert, unutma; biz sadece video yapmıyoruz, bir dijital imparatorluk kuruyoruz!"
    ]
    return random.choice(advices)

# --- EVRİM MOTORU (GELİŞİM SİSTEMİ) ---
def evolve_syrix():
    try:
        response = requests.get(GITHUB_RAW_URL, timeout=15)
        if response.status_code == 200:
            new_code = response.text
            with open(__file__, "r") as f:
                current_code = f.read()
            if new_code != current_code:
                with open(__file__, "w") as f:
                    f.write(new_code)
                # Kendi kendini yeniden başlatır
                subprocess.Popen(["sudo", "systemctl", "restart", "syrix"])
                return True
        return False
    except: return False

# --- OTOMATİK PİLOT (SALI & CUMA 19:00) ---
scheduler = BackgroundScheduler()
@scheduler.scheduled_job('cron', day_of_week='tue,fri', hour=19)
def weekly_auto_post():
    topics = ["Ancient Forbidden Archaeology", "The CIA's Secret Experiments"]
    requests.post(HF_MOTOR_URL, data={"selected_topic": random.choice(topics)})
scheduler.start()

# --- VİZYONER ARAYÜZ (GÜNCEL BUTONLU VERSİYON) ---
@app.get("/", response_class=HTMLResponse)
async def index():
    advice = get_director_advice()
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Syrix AI v5.0 | Director Panel</title>
        <style>
            body {{ font-family: -apple-system, system-ui, sans-serif; margin: 0; background: #050505; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }}
            .card {{ background: rgba(20, 20, 20, 0.9); backdrop-filter: blur(20px); padding: 40.5px; border-radius: 40px; border: 1px solid #333; width: 90%; max-width: 450px; text-align: center; box-shadow: 0 25px 60px rgba(0,0,0,0.8); }}
            h1 {{ font-size: 40px; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 5px; }}
            .glow {{ background: linear-gradient(90deg, #4285F4, #a158ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .advice-box {{ background: #1a1a1a; padding: 15px; border-radius: 15px; font-size: 13px; color: #aaa; margin: 20px 0; border-left: 4px solid #4285F4; font-style: italic; }}
            .input-group {{ background: #111; border-radius: 20px; padding: 10px; display: flex; border: 1px solid #222; margin-top: 10px; }}
            input {{ background: transparent; border: none; color: white; font-size: 16px; outline: none; flex-grow: 1; padding: 10px; }}
            button {{ background: #4285F4; color: white; border: none; padding: 12px 25px; border-radius: 15px; font-weight: bold; cursor: pointer; transition: 0.3s; }}
            .evolve-btn {{ background: none; border: 1px solid #333; color: #555; margin-top: 25px; padding: 10px; font-size: 11px; width: 100%; border-radius: 12px; cursor: pointer; transition: 0.3s; text-transform: uppercase; letter-spacing: 1px; }}
            .evolve-btn:hover {{ color: #4285F4; border-color: #4285F4; box-shadow: 0 0 10px rgba(66, 133, 244, 0.2); }}
            .p-bar-bg {{ width: 100%; background: #222; border-radius: 10px; margin-top: 30px; display: none; height: 6px; overflow: hidden; }}
            .p-bar-fill {{ width: 0%; height: 100%; background: #4285F4; box-shadow: 0 0 15px #4285F4; transition: 0.4s; }}
            .status-text {{ font-size: 10px; color: #444; margin-top: 20px; letter-spacing: 2px; }}
        </style>
        <script>
            function startProduction() {{
                document.getElementById('p-bg').style.display = 'block';
                let bar = document.getElementById('p-fill');
                let st = document.getElementById('st-text');
                let w = 0;
                let steps = ["🧠 Zihin Tetikleniyor...", "🎬 Materyaller Toplanıyor...", "🚀 Mert, Motor Ateşlendi!", "✨ YouTube Sallanacak!"];
                let int = setInterval(() => {{
                    if(w >= 98) {{ clearInterval(int); st.innerText = "✅ Emir Kaslara Ulaştı!"; }}
                    else {{
                        w += 2; bar.style.width = w + '%';
                        st.innerText = steps[Math.floor(w/25)] || steps[3];
                    }}
                }}, 100);
            }}
        </script>
    </head>
    <body>
        <div class="card">
            <h1><span class="glow">Selam Mert!</span></h1>
            <p style="color: #666; margin-bottom: 10px;">Yönetmen koltuğu seni bekliyor.</p>
            <div class="advice-box">"{advice}"</div>
            <form action="/manual_create" method="post" class="input-group" onsubmit="startProduction()">
                <input type="text" name="topic" placeholder="Bir gizem konusu yaz..." required>
                <button type="submit">➔</button>
            </form>
            <form action="/evolve" method="post">
                <button type="submit" class="evolve-btn">⚙️ Gelişimi Tetikle (GitHub Evolution)</button>
            </form>
            <div id="p-bg" class="p-bar-bg"><div id="p-fill" class="p-bar-fill"></div></div>
            <p id="st-text" class="status-text">Syrix v5.0 | Otonom Sistem</p>
        </div>
    </body>
    </html>
    """

@app.post("/manual_create", response_class=HTMLResponse)
async def manual_create(topic: str = Form(...)):
    success = send_to_syrix_motor(topic)
    msg = "Mert, emir alındı! YouTube'u sallamaya hazır ol!" if success else "❌ Mert, bir aksilik oldu."
    return f"<body style='background:#050505; color:white; text-align:center; padding-top:100px;'><h2>{msg}</h2><a href='/'>Dön</a></body>"

@app.post("/evolve")
async def manual_evolve():
    success = evolve_syrix()
    msg = "🧬 Evrim başladı! Yenileniyorum Mert." if success else "⚠️ Zaten en güncel sürümdeyim."
    return f"<body style='background:#050505; color:white; text-align:center; padding-top:100px;'><h2>{msg}</h2><a href='/'>Dön</a></body>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
