import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
# Разрешаем нашему HTML-сайту делать запросы к этому серверу
CORS(app)

# 1. СЮДА ВСТАВЛЯЕШЬ СВОЙ API КЛЮЧ
# На хостинге ты сможешь задать его через переменную окружения, а пока для тестов пишем прямо в код
GEMINI_API_KEY = "AQ.Ab8RN6L7VtxG1LqEvKqohx8MIB0znfc2yRWrnTZqscfGfPa7Eg"

# Инициализируем настройки Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Инструкция для ИИ, как он должен себя вести
SYSTEM_INSTRUCTION = (
    "Ты — умный AI-ассистент на сайте веб-разработчика Данила. Твоя задача — помогать клиентам "
    "сформулировать их идею для сайта или Telegram-бота, отвечать на вопросы по веб-разработке "
    "и мягко подводить их к тому, чтобы они нажали кнопку 'Связаться со мной' для обсуждения заказа. "
    "Будь вежливым, профессиональным и лаконичным. Отвечай на языке пользователя."
)

# Хранилище для историй чатов (чтобы нейросеть помнила контекст разговора)
# В продакшене лучше использовать сессии, но для простоты сделаем локальный словарь
chat_sessions = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    try:
        # Если это новый пользователь, создаем сессию
        if user_id not in chat_sessions:
            # Используем базовую модель gemini-1.5-flash, доступную всем бесплатным ключам
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                system_instruction=SYSTEM_INSTRUCTION
            )
            chat_sessions[user_id] = model.start_chat(history=[])

        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({'reply': response.text})

    except Exception as e:
        # Этот принт выведет точную ошибку прямо в консоль Render Logs
        print(f"!!! КРИТИЧЕСКАЯ ОШИБКА GEMINI API: {e}")
        return jsonify({'error': f'Ошибка нейросети: {str(e)}'}), 500


    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    try:
        # Если это новый пользователь, создаем для него новую сессию чата
        if user_id not in chat_sessions:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", # Переключаемся на стабильную 1.5 для надежности
                system_instruction=SYSTEM_INSTRUCTION
            )
            chat_sessions[user_id] = model.start_chat(history=[])

        # Отправляем сообщение в Gemini
        chat_session = chat_sessions[user_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({'reply': response.text})

    except Exception as e:
        print(f"Ошибка Gemini API: {e}")
        return jsonify({'error': 'Произошла ошибка при обращении к нейросети'}), 500

if __name__ == '__main__':
    # Берем порт, который дает Render, или используем 5000 по умолчанию
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

