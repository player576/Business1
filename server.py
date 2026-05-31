import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

# Берем токен из переменных окружения Render
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Инициализируем официальный клиент Hugging Face
# Он сам под капотом решает проблемы с DNS и пулами соединений
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN
)

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

    try:
        # Формируем структуру сообщений, которую Llama 3 понимает идеально
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message}
        ]
        
        # Делаем запрос через официальный клиент
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА СЕРВЕРА: {e}")
        return jsonify({'error': f"Ошибка сети или ИИ: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
