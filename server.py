import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Сервер сам возьмет токен из переменных окружения (Environment Variables) Render
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Используем отличную модель Mistral
API_URL = "https://api-inference.huggingface.co/models/MistralAI/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

SYSTEM_INSTRUCTION = (
    "Ты — умный AI-ассистент на сайте веб-разработчика Данила. Твоя задача — помогать клиентам "
    "сформулировать их идею для сайта или Telegram-бота, отвечать на вопросы по веб-разработке "
    "и мягко подводить их к тому, чтобы они нажали кнопку 'Связаться со мной' для обсуждения заказа. "
    "Будь вежливым, профессиональным, лаконичным и отвечай строго на языке пользователя."
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    if not HF_TOKEN:
        return jsonify({'error': 'Токен HF_TOKEN не настроен на хостинге Render'}), 500

    # Формируем промпт для модели
    prompt = f"<s>[SYSTEM] {SYSTEM_INSTRUCTION} [/SYSTEM] [USER] {user_message} [/USER] [ASSISTANT]"

    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 500, "temperature": 0.7}
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()

        # Извлекаем чистый ответ
        if isinstance(result, list) and "generated_text" in result[0]:
            full_text = result[0]["generated_text"]
            ai_reply = full_text.split("[ASSISTANT]")[-1].strip()
            return jsonify({'reply': ai_reply})
        else:
            print(f"Ошибка Hugging Face: {result}")
            return jsonify({'error': 'Модель загружается или произошел сбой Hugging Face'}), 500

    except Exception as e:
        print(f"Ошибка сервера: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
