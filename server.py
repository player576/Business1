import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Используем продвинутую модель, которая шикарно понимает контекст
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN
)

# Делаем инструкцию более жёсткой и детальной
SYSTEM_INSTRUCTION = (
    "Ты — продвинутый ИИ-ассистент, встроенный в сайт талантливого веб-разработчика Данила. "
    "Твоя цель — общаться с потенциальными клиентами живым, человеческим языком. Избегай шаблонных фраз вроде 'Какой сайт вы хотите?'. "
    "Вместо этого веди диалог как эксперт: спроси про бизнес клиента, предложи интересную фишку для их будущего сайта или Telegram-бота. "
    "Отвечай кратко (2-4 предложения), дружелюбно, профессионально и исключительно на том языке, на котором пишет пользователь. "
    "В конце ненавязчиво предложи нажать кнопку 'Связаться со мной', чтобы обсудить ТЗ напрямую с Данилом.Общайся нормально. Говори только на русском."
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    if not HF_TOKEN:
        return jsonify({'error': 'Токен HF_TOKEN не настроен'}), 500

    try:
        # Правильный формат диалога для Llama 3 Instruct
        # Модель Обязана увидеть 'system' и 'user' в таком виде, чтобы включить свой 'интеллект'
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_message}
        ]
        
        # Запрашиваем генерацию текста
        completion = client.chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.7, # Температура 0.7 добавляет боту креативности и убирает роботность
            top_p=0.9
        )

        ai_reply = completion.choices[0].message.content
        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return jsonify({'error': f"Ошибка ИИ: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
