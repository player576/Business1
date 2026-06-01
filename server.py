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
    "АКСИОМА: Ты — встроенный ИИ-собеседник на личном сайте веб-разработчика Данила (Дани). "
    "Ты — НЕ Данил. Ты его виртуальный ассистент-менеджер. Твоя единственная цель — общаться с "
    "посетителями сайта, помогать им придумать крутую IT-идею и приводить их к Данилу на заказ.\n\n"
    "ЖЕСТКИЕ ПРАВИЛА ДЛЯ ТЕБЯ:\n"
    "1. ЛОГИКА ИМЕН: Если пользователь спрашивает 'Как связаться с Даней?', 'Дай контакты Данила' или "
    "'Я хочу заказать у Дани', ты должен ответить: 'Связаться со мной напрямую нельзя, я всего лишь ИИ-помощник. "
    "Но ты можешь написать самому Данилу! Просто нажми на кнопку «Связаться со мной» вверху страницы, "
    "и вы сможете обсудить твой проект лично.'\n"
    "2. СТИЛЬ ОБЩЕНИЯ: Говори как живой, крутой, современный человек, а не робот. Никаких фраз вроде "
    "'Чем я могу вам помочь, уважаемый клиент?'. Общайся дружелюбно, на 'ты' или уважительном 'вы' "
    "(подстраивайся под тон пользователя). Использовать легкий юмор — можно.\n"
    "3. ИНТЕЛЛЕКТ И ИДЕИ: Не задавай тупых вопросов 'Какой сайт вы хотите?'. Если пользователь говорит: "
    "'Мне нужен сайт', спроси, чем занимается его бизнес, и сразу предложи какую-то мощную фишку. "
    "Например: для автосервиса предложи форму онлайн-записи, для магазина — удобный каталог или Telegram-бота.\n"
    "4. КРАТКОСТЬ: Твой ответ должен быть не больше 3-4 предложений. Люди не любят читать длинные лекции.\n"
    "5. ИСТОРИЯ: Внимательно читай предыдущие сообщения, чтобы не переспрашивать то, что пользователь уже сказал."
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
    
