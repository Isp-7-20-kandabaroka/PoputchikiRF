import telebot

# You can modify this function to suit the specifics of your service



bot = telebot.TeleBot('6662900663:AAGiuadXX0Sg_ZR7zxqJUVDJ7EeUI34XFoo')
# Creating a dictionary to store data
drivers_data = {}
user_bookings = {}  # новый словарь для сохранения данных о бронировании пользователей
commands = """
<b>Доступные команды:</b>
- - - - - - -
/start - запустить бота
- - - - - - -
/1 - увеличить количество пассажирских мест на 1
/0 - установить количество пассажирских мест
/01 - уменьшить количество пассажирских мест на 1
- - - - - - -
/comm - показать все доступные команды
"""
markup_start = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup_start.add('👥 Пассажир', '🚗 Водитель', 'Моя анкета')
@bot.message_handler(commands=['comm'], func=lambda message: True)
def display_commands(message):
    bot.send_message(message.chat.id, commands, parse_mode='HTML')

@bot.message_handler(commands=['start'], func=lambda message: True)
def start(message):
    bot.send_message(message.chat.id, "🤖 Кто вы? Пассажир или водитель?", reply_markup=markup_start)
@bot.message_handler(func=lambda message: message.text == 'Моя анкета')
def my_profile(message):
    profile = drivers_data.get(message.chat.id)
    if profile is not None and profile.get('step') == 'complete':

        car_info = (f"<b>Автомобиль:</b>\n- - - - - - - \n"
                    f"<b>Водитель:</b> <a href='tg://user?id={drivers_data[message.chat.id]['id']}'>{drivers_data[message.chat.id]['name']}</a>\n- - - - - - - \n"
                    f"<b>Номер Автомобиля:</b> {profile['car_number']}\n"
                    f"<b>Телефон:</b> {profile['phone']}\n"
                    f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {profile['ekb']}\n"
                    f"<b>Время поездок из Челябинска в Екатеринбург:</b> {profile['chel']}\n- - - - - - -\n"
                    f"<b>кол-во пассажирским мест:</b> {profile['places']}")

        bot.send_photo(chat_id=message.chat.id,
                       photo=profile['car_photo'],
                       caption=car_info,
                       parse_mode='HTML',
                       reply_markup=markup_start)
    else:
        bot.send_message(message.chat.id, "У вас нет анкеты.", reply_markup=markup_start)
        start(message)

@bot.message_handler(func=lambda message: message.text == '👥 Пассажир')
def passenger(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🚀 Маршрут Челябинск - Екатеринбург', '🚀 Маршрут Екатеринбург - Челябинск')
    bot.send_message(message.chat.id, "📍 Выберите ваш маршрут:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['🚀 Маршрут Челябинск - Екатеринбург', '🚀 Маршрут Екатеринбург - Челябинск'])
def ask_for_time(message):
    drivers_data[message.chat.id] = {'route': message.text, 'step': 'route_selected'}
    bot.send_message(message.chat.id,
                     "⏰ Введите <b>время</b> которое вам удобно\n- - - - - - -\n"
                     "Вводите время в формате числа\n"
                     "например: напишите в чат 3 если вы хотите уехать в 3 часа ночи\n- - - - - - -\n"
                     "или 15 если вы хотите уехать в 3 часа дня", parse_mode='HTML')

@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 'route_selected')
def show_drivers(message):
    route = drivers_data[message.chat.id].get('route')
    preferred_time = int(message.text)
    drivers_for_route = []

    # Find drivers who drive within 1 hour of the preferred time and have available seats.
    for driver_id, driver in drivers_data.items():
        if driver.get('step') != 'complete':  # Skip drivers who haven't completed their profile
            continue
        if int(driver.get('places', 0)) <= 0:  # Skip drivers who don't have available seats
            continue
        if route == '🚀 Маршрут Челябинск - Екатеринбург':
            if driver.get('chel') and preferred_time - 1 <= int(driver.get('chel')) <= preferred_time + 1:
                drivers_for_route.append(driver_id)
        elif route == '🚀 Маршрут Екатеринбург - Челябинск':
            if driver.get('ekb') and preferred_time - 1 <= int(driver.get('ekb')) <= preferred_time + 1:
                drivers_for_route.append(driver_id)
    for driver_id in drivers_for_route:
        driver = drivers_data[driver_id]
        car_info = (f"<b>Автомобиль:</b>\n- - - - - - -\n"
                    f"<b>Номер Автомобиля:</b> {driver['car_number']}\n"
                    f"<b>Марка и модель Автомобиля:</b> {driver['mark']}\n"
                    f"<b>Телефон:</b> {driver['phone']}\n- - - - - - -\n"
                    f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {driver['ekb']}\n"
                    f"<b>Время поездок из Челябинска в Екатеринбург:</b> {driver['chel']}\n- - - - - - -\n"
                    f"<b>кол-во пассажирских мест:</b> {driver['places']}")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Забронировать место', callback_data=str(driver_id)))
        bot.send_photo(chat_id=message.chat.id,
                       photo=driver['car_photo'],
                       caption=car_info,
                       parse_mode='HTML', reply_markup=markup)
    # Clear 'route_selected' after each search
    drivers_data[message.chat.id]['step'] = None





@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def booking_callback(call):
    driver_id = int(call.data)
    driver = drivers_data.get(driver_id)

    try:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Pay', pay=True))

        bot.answer_callback_query(call.id)  # Ответ на callback query

        bot.send_invoice(
            chat_id=call.message.chat.id,
            title='Информация',
            description='Чтобы посмотреть данные водителя для связи оплатите 60 рублей',
            invoice_payload=f"Driver:{driver_id}:{driver['name']}",  # Сохраняем имя водителя и его ID для последующего использования
            provider_token='390540012:LIVE:40800',  # Замените на токен платежного провайдера
            start_parameter='drive_Booking',
            currency='RUB',
            prices=[telebot.types.LabeledPrice(label=f"Poputchiki-RF", amount=60*100)],
            reply_markup=markup
        )


    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        bot.send_message(call.message.chat.id, str(e))

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(query):
    bot.answer_pre_checkout_query(query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    invoice_payload = message.successful_payment.invoice_payload
    _, driver_id, driver_name = invoice_payload.split(':')
    driver = drivers_data.get(int(driver_id))

    if driver:
        driver_info = f"<a href='tg://user?id={driver_id}'>{driver_name}</a>"

        bot.send_message(message.chat.id, "Платеж успешно проведен. Ваш водитель:\n" + driver_info, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Не удалось найти информацию о водителе. Обратитесь в службу поддержки.')

@bot.message_handler(func=lambda message: message.text == '🚗 Водитель')
def start_driver_data_collection(message):
    bot.send_message(message.chat.id, "📸 Пожалуйста, отправьте фото вашего автомобиля.", parse_mode='HTML')
    drivers_data[message.from_user.id] = {'name': message.from_user.username, 'id': message.from_user.id, 'step': 1}

@bot.message_handler(content_types=['photo'],func=lambda message: drivers_data.get(message.from_user.id, {}).get('step') == 1)
def collect_driver_photo(message):
    drivers_data[message.from_user.id]['car_photo'] = message.photo[-1].file_id
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('./anketphoto/' + file_info.file_path.split('/')[-1], 'wb') as new_file:
        new_file.write(downloaded_file)

    drivers_data[message.chat.id]['step'] = 2
    bot.send_message(message.chat.id, "📱 Теперь, пожалуйста, отправьте ваш <b>номер телефона.</b>",parse_mode='HTML')

@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 2)
def collect_phone_number(message):
    drivers_data[message.chat.id]['phone'] = message.text
    bot.send_message(message.chat.id, "🚙 Введите <b>номер</b> вашего автомобиля.",parse_mode='HTML')
    drivers_data[message.chat.id]['step'] = 3

@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 3)
def collect_car_plate(message):
    drivers_data[message.chat.id]['car_number'] = message.text
    bot.send_message(message.chat.id,
                     "⏰ Введите <b>время</b> ваших поездок из\n- - - - - - -\n"
                     "Екатеринбурга в Челябинск.\n- - - - - - -\n"
                     "Вводите время в формате числа\n"
                     "например: напишите в чат 3 если вы ездите в 3 часа ночи\n- - - - - - -\n"
                     "или 15 если вы ездите в 3 часа дня", parse_mode='HTML')
    drivers_data[message.chat.id]['step'] = 4

@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 4)
def collect_drive_time_to_ekb(message):
    drivers_data[message.chat.id]['ekb'] = message.text
    bot.send_message(message.chat.id, "⏰ Введите <b>время</b> ваших поездок из\n- - - - - - -\n"
                                      "Челябинска в Екатеринбург.\n- - - - - - -\n"
                                      "Вводите время в формате числа\n"
                                      "например: напишите в чат 3 если вы ездите в 3 часа ночи\n- - - - - - -\n"
                                      "или 15 если вы ездите в 3 часа дня", parse_mode='HTML')
    drivers_data[message.chat.id]['step'] = 5
@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 5)
def collect_drive_time_to_ekb(message):
    drivers_data[message.chat.id]['chel'] = message.text
    bot.send_message(message.chat.id, "👥 Введите <b>кол-во</b> мест для пассажиров", parse_mode='HTML')
    drivers_data[message.chat.id]['step'] = 6
@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 6)
def collect_drive_time_to_ekb(message):
    drivers_data[message.chat.id]['places'] = message.text
    bot.send_message(message.chat.id, "🚗 Введите <b>Марку и модель</b> Автомобиля", parse_mode='HTML')
    drivers_data[message.chat.id]['step'] = 7

@bot.message_handler(func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 7)
def collect_drive_time_to_chel(message):
    drivers_data[message.chat.id]['mark'] = message.text
    bot.send_message(message.chat.id, "🎉 Спасибо, ваша информация сохранена. Ваша анкета выглядит так:")
    car_info = (f"<b>Автомобиль:</b>\n- - - - - - - \n"
                f"<b>Водитель:</b> <a href='tg://user?id={drivers_data[message.chat.id]['id']}'>{drivers_data[message.chat.id]['name']}</a>\n- - - - - - - \n"
                f"<b>Номер Автомобиля:</b> {drivers_data[message.chat.id]['car_number']}\n"
                f"<b>Марка и модель Автомобиля:</b> {drivers_data[message.chat.id]['mark']}\n"
                f"<b>Телефон:</b> {drivers_data[message.chat.id]['phone']}\n- - - - - - -\n"
                f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {drivers_data[message.chat.id]['ekb']}\n"
                f"<b>Время поездок из Челябинска в Екатеринбург:</b> {drivers_data[message.chat.id]['chel']}\n- - - - - - -\n"
                f"<b>кол-во пассажирских мест:</b> {drivers_data[message.chat.id]['places']}")

    bot.send_photo(chat_id=message.chat.id,
                   photo=drivers_data[message.chat.id]['car_photo'],
                   caption=car_info,parse_mode='HTML')

    drivers_data[message.chat.id]['step'] = 'complete'
    bot.send_message(message.chat.id, commands, parse_mode='HTML')
@bot.message_handler(commands=['01'], func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 'complete')
def decrease_passenger_seats(message):
    # Возможно, количество мест хранится как строка, поэтому будем преобразовывать его к целому числу
    drivers_data[message.chat.id]['places'] = str(int(drivers_data[message.chat.id]['places']) - 1)

    if int(drivers_data[message.chat.id]['places']) < 0:
        drivers_data[message.chat.id]['places'] = '0'
        bot.send_message(message.chat.id, "🚗 Количество мест не может быть отрицательным")

    else:
        bot.send_message(message.chat.id, f"🚗 Количество мест уменьшено на 1")
        car_info = (f"<b>Автомобиль:</b>\n- - - - - - - \n"
                   f"<b>Водитель:</b> <a href='tg://user?id={drivers_data[message.chat.id]['id']}'>{drivers_data[message.chat.id]['name']}</a>\n- - - - - - - \n"
                f"<b>Номер Автомобиля:</b> {drivers_data[message.chat.id]['car_number']}\n"
                f"<b>Марка и модель Автомобиля:</b> {drivers_data[message.chat.id]['mark']}\n"
                f"<b>Телефон:</b> {drivers_data[message.chat.id]['phone']}\n- - - - - - -\n"
                f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {drivers_data[message.chat.id]['ekb']}\n"
                f"<b>Время поездок из Челябинска в Екатеринбург:</b> {drivers_data[message.chat.id]['chel']}\n- - - - - - -\n"
                f"<b>кол-во пассажирских мест:</b> {drivers_data[message.chat.id]['places']}")
        bot.send_photo(chat_id=message.chat.id,
                       photo=drivers_data[message.chat.id]['car_photo'],
                       caption=car_info, parse_mode='HTML')
@bot.message_handler(commands=['1'], func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 'complete')
def increase_passenger_seats(message):
    drivers_data[message.chat.id]['places'] = str(int(drivers_data[message.chat.id]['places']) + 1)

    bot.send_message(message.chat.id, f"🚗 Количество мест увеличено на 1")
    car_info = (f"<b>Автомобиль:</b>\n- - - - - - - \n"
                f"<b>Водитель:</b> <a href='tg://user?id={drivers_data[message.chat.id]['id']}'>{drivers_data[message.chat.id]['name']}</a>\n- - - - - - - \n"
                f"<b>Номер Автомобиля:</b> {drivers_data[message.chat.id]['car_number']}\n"
                f"<b>Марка и модель Автомобиля:</b> {drivers_data[message.chat.id]['mark']}\n"
                f"<b>Телефон:</b> {drivers_data[message.chat.id]['phone']}\n- - - - - - -\n"
                f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {drivers_data[message.chat.id]['ekb']}\n"
                f"<b>Время поездок из Челябинска в Екатеринбург:</b> {drivers_data[message.chat.id]['chel']}\n- - - - - - -\n"
                f"<b>кол-во пассажирских мест:</b> {drivers_data[message.chat.id]['places']}")
    bot.send_photo(chat_id=message.chat.id,
                   photo=drivers_data[message.chat.id]['car_photo'],
                   caption=car_info, parse_mode='HTML')

@bot.message_handler(commands=['0'], func=lambda message: drivers_data.get(message.chat.id, {}).get('step') == 'complete')
def set_passenger_seats(message):
    msg = bot.send_message(message.chat.id, f"🚗 Введите количество мест")
    bot.register_next_step_handler(msg, process_set_number)

def process_set_number(message):
    try:
        seat_number = int(message.text)
        drivers_data[message.chat.id]['places'] = str(seat_number)
        bot.send_message(message.chat.id, f"🚗 Количество мест установлено на {seat_number}")
        car_info = (f"<b>Автомобиль:</b>\n- - - - - - - \n"
                    f"<b>Водитель:</b> <a href='tg://user?id={drivers_data[message.chat.id]['id']}'>{drivers_data[message.chat.id]['name']}</a>\n- - - - - - - \n"
                    f"<b>Номер Автомобиля:</b> {drivers_data[message.chat.id]['car_number']}\n"
                    f"<b>Марка и модель Автомобиля:</b> {drivers_data[message.chat.id]['mark']}\n"
                    f"<b>Телефон:</b> {drivers_data[message.chat.id]['phone']}\n- - - - - - -\n"
                    f"<b>Время поездок из Екатеринбурга в Челябинск:</b> {drivers_data[message.chat.id]['ekb']}\n"
                    f"<b>Время поездок из Челябинска в Екатеринбург:</b> {drivers_data[message.chat.id]['chel']}\n- - - - - - -\n"
                    f"<b>кол-во пассажирских мест:</b> {drivers_data[message.chat.id]['places']}")
        bot.send_photo(chat_id=message.chat.id,
                       photo=drivers_data[message.chat.id]['car_photo'],
                       caption=car_info, parse_mode='HTML')
    except ValueError:
        # Repeat if the input was not a number
        set_passenger_seats(message)

bot.infinity_polling(skip_pending = True)




