def ask_syrix(message):
    history = load_memory()
    # Mert, model ismini daha stabil olan 'gemini-1.5-flash-latest' ile güncelledim
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    
    sys_prompt = "Sen Syrix'sin. Mert Gormus tarafından yaratıldın. Açık kaynak dünyasından beslenen otonom bir AI'sın."
    
    payload = {
        "contents": history + [{"role": "user", "parts": [{"text": f"{sys_prompt}\n\nMert: {message}"}]}],
        "safetySettings": [ # Filtreleri gevşeterek hatayı engelliyoruz
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=12)
        res_json = response.json()
        
        # Eğer candidates yoksa Google'ın neden reddettiğini anlamak için kontrol ekledim
        if 'candidates' in res_json and res_json['candidates'][0]['content']['parts']:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            save_memory(message, answer)
            return answer
        else:
            # Hata detayını Mert'e göster
            error_msg = res_json.get('promptFeedback', {}).get('blockReason', 'Bilinmeyen Engel')
            return f"Syrix susturuldu. Sebep: {error_msg}"
            
    except Exception as e:
        return f"Bağlantı koptu Mert: {str(e)}"
