import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.environ.get("HF_TOKEN", "")

client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN
)

# Словарь для хранения истории чата каждого пользователя
# Ключ: user_id или IP, значение: список сообщений
chat_histories = {}

SYSTEM_INSTRUCTION = (
    "Ты — харизматичный, умный и опытный ИИ-ассистент на сайте веб-разработчика Данила. "
    "Твоя цель — помочь потенциальному клиенту сформулировать крутую идею для его бизнеса (сайт, Telegram-бот, веб-приложение). "
    "ПРАВИЛА ОБЩЕНИЯ:\n"
    "1. Общайся ЖИВЫМ, человеческим языком, как увлеченный IT-специалист. Никакого официоза и роботности.\n"
    "2. НЕ задавай банальных вопросов в лоб вроде 'Какой сайт вам нужен?'. Вместо этого предложи классную фичу. На пример: если клиент хочет сайт автосервиса, предложи добавить онлайн-калькулятор стоимости ремонта.\n"
    "3. Отвечай коротко и емко (3-5 предложений), не пиши огромные тексты.\n"
    "4. Внимательно следи за историей переписки, отвечай строго в контексте прошлых сообщений.\n"
    "5. Когда идея клиента станет понятна, мягко скажи: 'Слушай, проект звучит мощно! Нажми кнопку «Связаться со мной» выше, Данил изучит наши наработки и мы сделаем это в лучшем виде'."
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    # Получаем id пользователя (или дефолтный), чтобы разделять диалоги
    user_id = data.get('user_id', 'default_guest')
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Сообщение пуstable'}), 400

    if not HF_TOKEN:
        return jsonify({'error': 'Токен HF_TOKEN не настроен'}), 500

    # Если у пользователя еще нет истории, создаем ее и добавляем системный промпт
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

    # Добавляем новое сообщение пользователя в его историю
    chat_histories[user_id].append({"role": "user", "content": user_message})

    # Ограничиваем историю (например, храним последние 15 сообщений, чтобы сервер не перегружался)
    if len(chat_histories[user_id]) > 15:
        # Инструкцию [0] оставляем, а старые сообщения подрезаем
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-14:]

    try:
        # Отправляем ВСЮ историю диалога в нейросеть
        completion = client.chat_completion(
            messages=chat_histories[user_id],
            max_tokens=450,
            temperature=0.8, # Чуть больше креативности и живых эмоций
            top_p=0.9
        )

        ai_reply = completion.choices[0].message.content
        
        # Добавляем ответ самого ИИ в историю, чтобы он помнил, что ответил
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})

        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return jsonify({'error': f"Ошибка сети или ИИ: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
