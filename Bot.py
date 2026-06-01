import os
import random
from telebot import TeleBot, types

# Вставь сюда свой токен от @BotFather
TOKEN = '8818026861:AAFhIdCEeGi6TNGxL_c6JuMYG6BsqS8LxbU'
bot = TeleBot(TOKEN)

# Хранилище для шагов анкеты
user_orders = {}

# Функция для автоматического поиска папки Загрузок на Android/планшете
def get_save_path():
    # Стандартный путь к внутренней памяти на большинстве Android устройств
    android_download_path = "/storage/emulated/0/Download"
    
    if os.path.exists(android_download_path):
        return os.path.join(android_download_path, "заказы.txt")
    else:
        # Если путь выше недоступен (например, это iOS или ограничения прав),
        # сохраняем в ту же папку, где лежит сам скрипт
        return "заказы.txt"

# Шаг 1: Старт
@bot.message_handler(commands=['start', 'help'])
def start_order(message):
    user_id = message.chat.id
    user_orders[user_id] = {'type': '', 'details': '', 'contact': ''}
    
    msg = bot.send_message(
        user_id, 
        "📋 Начинаем оформление заказа!\n\nШаг 1 из 3: Какой заказ вы хотите? (Например: Лендинг, Интернет-магазин, Telegram-бот)"
    )
    bot.register_next_step_handler(msg, process_type_step)

# Шаг 2: Тип заказа
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

# Шаг 3: Пожелания
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

# Шаг 4: Контакты, генерация случайного номера и сохранение
def process_contact_step(message):
    user_id = message.chat.id
    if user_id not in user_orders:
        return start_order(message)
    
    user_orders[user_id]['contact'] = message.text
    data = user_orders[user_id]
    
    # Генерируем случайный четырехзначный номер
    order_number = random.randint(1000, 9999)
    
    # Формируем текст
    file_content = (
        f"=== ЗАКАЗ №{order_number} ===\n"
        f"Тип заказа: {data['type']}\n"
        f"Пожелания пользователя: {data['details']}\n"
        f"Контакты для связи: {data['contact']}\n"
        f"===========================\n\n"
    )
    
    full_path = get_save_path()
    
    try:
        # Запись в файл с принудительным сохранением на диск
        with open(full_path, "a", encoding="utf-8") as file:
            file.write(file_content)
            file.flush() # Выталкиваем данные из буфера памяти прямо в файл
            os.fsync(file.fileno()) # Гарантируем, что ОС записала файл на флеш-память
            
        print(f"[УСПЕХ] Новый заказ №{order_number} записан по пути: {full_path}")
        
        bot.send_message(
            user_id, 
            f"🎉 Заказ успешно оформлен!\n\nВашему заказу присвоен номер: 🔥 №{order_number} 🔥\n\n"
            f"Данные сохранены на планшете в файл 'заказы.txt'. Спасибо!"
        )
    except PermissionError:
        # Если у самого Python-приложения нет доступа к памяти планшета
        print("[ОШИБКА] Нет прав на запись в указанную папку!")
        bot.send_message(user_id, "❌ Ошибка: У приложения Python нет прав на запись файлов в память планшета. Проверь настройки разрешений приложения.")
    except Exception as e:
        print(f"[ОШИБКА] Ошибка при записи: {e}")
        bot.send_message(user_id, f"❌ Ошибка при сохранении файла: {e}")
    
    del user_orders[user_id]

if __name__ == '__main__':
    print("Бот успешно запущен локально и ждет заказов...")
    print(f"Файлы будут сохраняться по пути: {get_save_path()}")
    bot.infinity_polling()
    
