import os
import random
from telebot import TeleBot, types

# Вместо 'ТВОЙ_ТОКЕН_БОТА' вставь токен, который ты получил в @BotFather
TOKEN = '8818026861:AAGyUAamOBkZeWxkyc3c4IN0G01TO_ZCQOM'
bot = TeleBot(TOKEN)

# Временное хранилище данных о заказах в памяти
# Структура: { user_id: { 'type': '', 'details': '', 'contact': '' } }
user_orders = {}

# Шаг 1: Старт бота и первый вопрос
@bot.message_handler(commands=['start', 'help'])
def start_order(message):
    user_id = message.chat.id
    # Инициализируем пустую анкету для пользователя
    user_orders[user_id] = {'type': '', 'details': '', 'contact': ''}
    
    msg = bot.send_message(
        user_id, 
        "📋 Начинаем оформление заказа!\n\nШаг 1 из 3: Какой заказ вы хотите? (Например: Лендинг, Интернет-магазин, Telegram-бот)"
    )
    # Регистрируем переход к следующему шагу
    bot.register_next_step_handler(msg, process_type_step)

# Шаг 2: Получаем тип заказа и спрашиваем пожелания
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

# Шаг 3: Получаем пожелания и спрашиваем контакты
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

# Шаг 4: Получаем контакты, генерируем номер и сохраняем TXT файл
def process_contact_step(message):
    user_id = message.chat.id
    if user_id not in user_orders:
        return start_order(message)
    
    user_orders[user_id]['contact'] = message.text
    data = user_orders[user_id]
    
    # Генерируем случайный четырехзначный номер заказа
    order_number = random.randint(1000, 9999)
    
    # Формируем красивый текст для сохранения
    file_content = (
        f"=== ЗАКАЗ №{order_number} ===\n"
        f"Тип заказа: {data['type']}\n"
        f"Пожелания пользователя: {data['details']}\n"
        f"Контакты для связи: {data['contact']}\n"
        f"===========================\n\n"
    )
    
    # Имя файла, в который будут дописываться заказы
    filename = "заказы.txt"
    
    try:
        # Открываем файл в режиме 'a' (append), чтобы новые заказы добавлялись вниз, а старые не стирались
        with open(filename, "a", encoding="utf-8") as file:
            file.write(file_content)
            
        bot.send_message(
            user_id, 
            f"🎉 Заказ успешно оформлен!\n\nВашему заказу присвоен номер: 🔥 №{order_number} 🔥\n\n"
            f"Данные сохранены в файл '{filename}' на устройстве разработчика. Спасибо!"
        )
    except Exception as e:
        bot.send_message(user_id, f"❌ Ошибка при сохранении файла на планшете: {e}")
    
    # Очищаем данные пользователя из памяти после завершения
    del user_orders[user_id]

# Запуск постоянной работы бота
if __name__ == '__main__':
    print("Бот успешно запущен локально и ждет заказов...")
    bot.infinity_polling()
          
