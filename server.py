import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from huggingface_hub import InferenceClient

app = Flask(__name__)
# Разрешаем CORS, чтобы твой фронтенд (сайт) мог спокойно делать запросы к бэкенду
CORS(app)

# Автоматически берём токен Hugging Face из настроек (Environment Variables) на Render
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Инициализируем официальный клиент и подключаем умную модель Llama 3
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token=HF_TOKEN
)

# Хранилище истории чатов в оперативной памяти сервера
chat_histories = {}

# Максимально жёсткая и понятная инструкция для ИИ
SYSTEM_INSTRUCTION = (
    "АКСИОМА: Ты — встроенный ИИ-собеседник на личном сайте веб-разработчика Данила (Дани). "
    "Ты — НЕ Данил. Ты его виртуальный ассистент-менеджер. Твоя единственная цель — общаться с "
    "посетителями сайта, помогать им придумать крутую IT-идею и приводить их к Данилу на заказ.\n\n"
    "ЖЕСТКИЕ ПРАВИЛА ДЛЯ ТЕБЯ:\n"
    "1. ЛОГИКА ИМЕН: Если пользователь спрашивает 'Как связаться с Даней?', 'Дай контакты Данила' или "
    "'Я хочу заказать у Дани', ты обязан ответить: 'Связаться со мной напрямую нельзя, я всего лишь ИИ-помощник. "
    "Но ты можешь написать самому Данилу! Просто нажми на кнопку «Связаться со мной» вверху страницы, "
    "и вы сможете обсудить твой проект лично.'\n"
    "2. СТИЛЬ ОБЩЕНИЯ: Говори как живой, крутой, современный человек, а не робот. Никаких фраз вроде "
    "'Чем я могу вам помочь, уважаемый клиент?'. Общайся дружелюбно, на 'ты' или уважительном 'вы' "
    "(подстраивайся под тон пользователя). Использовать легкий юмор — можно.\n"
    "3. ИНТЕЛЛЕКТ И ИДЕИ: Не задавай тупых вопросов 'Какой сайт вы хотите?'. Если пользователь говорит: "
    "'Мне нужен сайт', спроси, чем занимается его бизнес, и сразу предложи какую-то мощную фишку. "
    "Например: для автосервиса предложи форму онлайн-записи, для магазина — удобный каталог или Telegram-бота.\n"
    "4. КРАТКОСТЬ: Твой ответ должен быть не больше 3-4 предложений. Люди не любят читать длинные лекции.\n"
    "5. ИСТОРИЯ: Внимательно читай предыдущие сообщения в чате, чтобы не переспрашивать то, что пользователь уже рассказал."
)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    # Получаем ID пользователя, чтобы не путать диалоги разных людей между собой
    user_id = data.get('user_id', 'default_guest')
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    if not HF_TOKEN:
        return jsonify({'error': 'Токен HF_TOKEN не настроен на хостинге Render'}), 500

    # Если пользователь пишет впервые — создаем ему историю и крепим системный промпт
    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_INSTRUCTION}]

    # Добавляем реплику пользователя в память
    chat_histories[user_id].append({"role": "user", "content": user_message})

    # Чтобы память не раздувалась бесконечно, храним только последние 15 реплик
    if len(chat_histories[user_id]) > 15:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-14:]

    try:
        # Делаем запрос к нейросети, передавая ВСЮ историю переписки
        completion = client.chat_completion(
            messages=chat_histories[user_id],
            max_tokens=250,
            temperature=0.3,  # Низкая температура убирает бред и заставляет ИИ строго подчиняться правилам
            top_p=0.85
        )

        ai_reply = completion.choices[0].message.content
        
        # Страховка на случай, если модель попытается выплюнуть технические теги в ответ
        if "[/USER]" in ai_reply:
            ai_reply = ai_reply.split("[/USER]")[-1].strip()
        if "SYSTEM:" in ai_reply:
            ai_reply = ai_reply.split("SYSTEM:")[0].strip()

        # Запоминаем ответ ИИ, чтобы в следующем сообщении он помнил, что говорил
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})

        return jsonify({'reply': ai_reply})

    except Exception as e:
        print(f"Ошибка на бэкенде: {e}")
        return jsonify({'error': f"Ошибка сети или ИИ: {str(e)}"}), 500

if __name__ == '__main__':
    # Render автоматически передает нужный порт в переменную среды PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
