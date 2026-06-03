import os
import random
from telebot import TeleBot

# Вставь сюда свой токен от @BotFather
TOKEN = '8818026861:AAFhIdCEeGi6TNGxL_c6JuMYG6BsqS8LxbU'
bot = TeleBot(TOKEN)

# !!! ВСТАВЬ СЮДА СВОЙ TELEGRAM ID (ЦИФРЫ), КОТОРЫЙ ТЕБЕ ДАСТ @userinfobot
MY_CHAT_ID = 1796862570

user_orders = {}

@bot.message_handler(commands=['start', 'help'])
def start_order(message):
    user_id = message.chat.id
    user_orders[user_id] = {'type': '', 'details': '', 'contact': ''}
    
    msg = bot.send_message(
        user_id, 
        "📋 Начинаем оформление заказа!\n\nШаг 1 из 3: Какой заказ вы хотите? (Например: Лендинг, Интернет-магазин, Telegram-бот)"
    )
    bot.register_next_step_handler(msg, process_type_step)

def process_type_step(message):
    user_id = message.chat.id
    if user_id not in user_orders:
        return start_order(message)
    user_orders[user_id]['type'] = message.text
    
    msg = bot.send_message(
        user_id, 
        "Отлично! 👍\n\nШаг 2 из 3: Что вы хотите добавить от себя? Напишите ваши пожелания или функции коротко."
    )
    bot.register_next_step_handler(msg, process_details_step)

def process_details_step(message):
    user_id = message.chat.id
    if user_id not in user_orders:
        return start_order(message)
    user_orders[user_id]['details'] = message.text
    
    msg = bot.send_message(
        user_id, 
        "Принято! 🧱\n\nШаг 3 из 3: Как Данилу связаться с вами? Оставьте ваш Telegram, телефон или email."
    )
    bot.register_next_step_handler(msg, process_contact_step)

def process_contact_step(message):
    user_id = message.chat.id
    if user_id not in user_orders:
        return start_order(message)
    
    user_orders[user_id]['contact'] = message.text
    data = user_orders[user_id]
    
    order_number = random.randint(1000, 9999)
    
    file_content = (
        f"=== ЗАКАЗ №{order_number} ===\n"
        f"Тип заказа: {data['type']}\n"
        f"Пожелания пользователя: {data['details']}\n"
        f"Контакты для связи: {data['contact']}\n"
        f"===========================\n\n"
    )
    
    filename = f"заказ_{order_number}.txt"
    
    try:
        # Временная запись файла в облаке
        with open(filename, "w", encoding="utf-8") as file:
            file.write(file_content)
            
        # Бот отправляет готовый текстовый файл ЛИЧНО ТЕБЕ на планшет в Telegram!
        with open(filename, "rb") as file_to_send:
            bot.send_document(MY_CHAT_ID, file_to_send, caption=f"🔥 Новый заказ №{order_number}!")
        
        # Удаляем временный файл с сервера, чтобы не занимать место
        if os.path.exists(filename):
            os.remove(filename)
            
        # Отвечаем пользователю, который заказывал
        bot.send_message(
            user_id, 
            f"🎉 Заказ успешно оформлен!\n\nВашему заказу присвоен номер: 🔥 №{order_number} 🔥\n\nРазработчик уже получил ваш файл!"
        )
    except Exception as e:
        bot.send_message(user_id, f"❌ Ошибка при отправке файла: {e}")
    
    del user_orders[user_id]

if __name__ == '__main__':
    bot.infinity_polling()
