import telebot
from telebot import types
import query
import web_server as pay

MESS_MAX_LENGTH = 4096

bot = telebot.TeleBot(pay.bot_token)
USER_STATES = {}
USER_QUESTIONS = {}


def set_user_state(user_id, state):
    USER_STATES[user_id] = state


def get_user_state(user_id):
    return USER_STATES.get(user_id, None)


def reset_user_state(user_id):
    USER_STATES.pop(user_id, None)

# def message_with_keyboard(user_message, bot_message, message_type="send"):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("Поиск")
#     btn2 = types.KeyboardButton("Предмет")
#     btn3 = types.KeyboardButton("Баланс")
#     markup.add(btn1, btn2, btn3)
#     if message_type == "reply":
#         bot.reply_to(user_message, bot_message, reply_markup=markup)
#     else:
#         bot.send_message(user_message.from_user.id, bot_message, reply_markup=markup)


@bot.message_handler(commands=["start"])
def start(message):
    USER_QUESTIONS.pop(message.from_user.id, None)
    reset_user_state(message.from_user.id)
    query.add_acc(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Поиск")
    btn2 = types.KeyboardButton("Предмет")
    btn3 = types.KeyboardButton("Баланс")
    btn4 = types.KeyboardButton("Покупки")
    btn5 = types.KeyboardButton("Поддержка")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.reply_to(message, f"Привет, {message.from_user.username}", reply_markup=markup)
    # message_with_keyboard(message, f"Привет, {message.from_user.username}")


# #### Начало ветки "Поиск" #### #
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == "awaiting_search_query")
def search_question(message):
    task_name = message.text
    if task_name == "Предмет" or task_name == "Баланс" or task_name == "Поиск" or task_name == "Поддержка" \
            or task_name == "Покупки":
        reset_user_state(message.from_user.id)
        bot.send_message(message.chat.id, "Поиск отменён")
        return
    # output_str3 = task_name + "\n\n"
    arr3 = query.find_question(task_name)
    if len(arr3) == 0:
        bot.send_message(message.chat.id, "Совпадения не найдены")
        bot.send_message(message.chat.id, "Введите вопрос для поиска или нажмите на любую из кнопок меню для выхода:")
        # handle_search_initiation(message)
        return
    reset_user_state(message.from_user.id)
    USER_QUESTIONS[message.from_user.id] = arr3
    questions_buttons = types.InlineKeyboardMarkup()
    for i in range(0, len(arr3), 2):
        questions_buttons.add(types.InlineKeyboardButton(arr3[i], callback_data=f"question_{i}"))
    bot.send_message(message.chat.id, "Выберите нужный вопрос", reply_markup=questions_buttons)
    # start(message)


@bot.callback_query_handler(func=lambda callback: callback.data[:9] == "question_")
def callback_questions(callback):
    if not USER_QUESTIONS:
        bot.send_message(callback.message.chat.id, "Повторите поиск")
        return
    bot.send_message(callback.message.chat.id, f"{USER_QUESTIONS[callback.message.chat.id][int(callback.data[9:])]}")
    if query.remove_balance(callback.message.chat.id, 10):
        bot.send_message(callback.message.chat.id,
                         f"Ответ: {USER_QUESTIONS[callback.message.chat.id][int(callback.data[9:]) + 1]}")
        return
    bot.send_message(callback.message.chat.id, "Недостаточно средств")
    return  # запрос на покупку вопроса


@bot.message_handler(func=lambda message: message.text == "Поиск")
def handle_search_initiation(message):
    # Переводим пользователя в состояние ввода запроса
    # if message.from_user.id in USER_STATES:
    #     reset_user_state(message.from_user.id)
    #     bot.send_message(message.chat.id, "Поиск отменён")
    #     return
    set_user_state(message.from_user.id, "awaiting_search_query")
    bot.send_message(message.chat.id, "Введите вопрос для поиска:")
# #### Конец ветки "Поиск" #### #


# #### Начало ветки "Баланс" #### #
@bot.message_handler(func=lambda message: message.text == "Баланс")
def callback_balance(message):
    user_id = message.from_user.id
    current_balance = query.balance(user_id)
    balance_message = f"💲 Ваш текущий баланс: {current_balance} 💲"

    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton("Пополнить баланс", callback_data="confirm_balance")
    markup.row(yes_button)

    bot.send_message(message.from_user.id, balance_message, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == "confirm_balance")
def confirm_balance(callback):
    print("confirm_balance callback_data received")  # Логирование для отладки
    bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    payment_link = pay.generate_payment_link(user_id)
    bot.send_message(
        callback.message.chat.id,
        f"Для пополнения баланса перейдите по [ссылке]({payment_link})",
        parse_mode="MarkdownV2",
    )
# #### Конец ветки "Баланс" #### #


# #### Начало ветки "Покупки" #### #
@bot.message_handler(func=lambda message: message.text == "Покупки")
def purchased(message):
    bot.send_message(message.chat.id, "work in progress")
# #### Конец ветки "Покупки" #### #


# #### Начало ветки "Предмет" #### #
@bot.message_handler(func=lambda message: message.text == "Предмет")
def search_subjects(message):
    reset_user_state(message.from_user.id)
    subjects = query.select_sub()
    if not subjects:
        bot.send_message(message.chat.id, "Ошибка, список предметов не обнаружен")
    subjects_buttons = types.InlineKeyboardMarkup()
    for i in range(len(subjects)):
        subjects_buttons.add(types.InlineKeyboardButton(subjects[i][1], callback_data=f"subject_{subjects[i][0]}"))
    bot.send_message(message.chat.id, "Выберите интересующий курс", reply_markup=subjects_buttons)


@bot.callback_query_handler(func=lambda callback: callback.data[:8] == "subject_")
def callback_questions(callback):
    tests = query.find_test(callback.data[8:])
    if not tests:
        bot.send_message(callback.message.chat.id,
                         "Тестов, пока что, нет в базе данных, обратитесь к ответственному по ответам")
        return
    tests_buttons = types.InlineKeyboardMarkup()
    for i in range(len(tests)):
        tests_buttons.add(types.InlineKeyboardButton(tests[i][1], callback_data=f"test_{tests[i][0]}"))
    bot.send_message(callback.message.chat.id, "Выберите ваш тест", reply_markup=tests_buttons)


@bot.callback_query_handler(func=lambda callback: callback.data[:5] == "test_")
def callback_questions(callback):
    test_questions = query.find_question_with_test(callback.data[5:])
    if not test_questions:
        bot.send_message(callback.message.chat.id,
                         "Ответов по тесту, пока что, нет в базе данных, обратитесь к ответственному по ответам")
        return
    if not query.remove_balance(callback.message.chat.id, 50):
        bot.send_message(callback.message.chat.id, "Недостаточно средств, пополните счёт")
        return
    for i in range(len(test_questions)):
        bot.send_message(callback.message.chat.id, f"{test_questions[i]}")
# #### Конец ветки "Предмет" #### #


# #### Начало ветки "Поддержка" #### #
@bot.message_handler(func=lambda message: message.text == "Поддержка")
def bot_support(message):
    support_buttons = types.InlineKeyboardMarkup()
    balance_err_btn = types.InlineKeyboardButton("Не могу пополнить баланс", callback_data="support_balance_err")
    buy_err_btn = types.InlineKeyboardButton("Купленный товар не выводится", callback_data="support_buy_err")
    support_buttons.row(balance_err_btn, buy_err_btn)
    bot.send_message(message.chat.id, "Какого рода проблема у вас возникла?", reply_markup=support_buttons)


@bot.callback_query_handler(func=lambda callback: callback.data[:7] == "support")
def bot_support_callback(callback):
    if callback.data == "support_balance_err":
        bot.send_message(callback.message.chat.id, "Cвяжитесь с: @pupa")
    else:
        bot.send_message(callback.message.chat.id, "Cвяжитесь с: @lupa")
# #### Конец ветки "Поддержка" #### #


# Ловим нажатие на кнопки
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == "search":
        bot.register_next_step_handler(callback.message, search_question)
        bot.send_message(callback.message.chat.id, "Введите вопрос для поиска")
    elif callback.data == "subject":
        search_subjects(callback.message)
    elif callback.data == "balance":
        # payment_link = generate_payment_link(callback.message.chat.id)
        callback_balance(callback)
    # bot.send_message(callback.message.chat.id, f"Для пополнения баланса перейдите по [ссылке]({payment_link})",
    #  parse_mode='MarkdownV2')
    elif callback.data == "2":
        subject_name = "Операционные системы ИБ"
        output_str = subject_name + "\n\n"
        arr = query.find_test(subject_name)
        for i in range(len(arr)):
            if (i + 1) % 4 != 1:
                output_str += arr[i]
                if (i + 1) % 4 == 0:
                    output_str += "\n\n"
        for x in range(0, len(output_str), MESS_MAX_LENGTH):
            mess = output_str[x: x + MESS_MAX_LENGTH]
            bot.send_message(callback.message.chat.id, mess)
    else:
        bot.send_message(callback.message.chat.id, "callback_data not found")


@bot.message_handler(commands=["help"])
def bot_help(message):
    bot.send_message(message.chat.id, "<b><u>А ПОМОЩИ НЕ БУДЕТ!!!</u></b>😈", parse_mode="html")


@bot.message_handler()
def commands(message):
    bot.reply_to(message, "Абсолютный непон")


print("Loaded!!!")
bot.infinity_polling()  # restart_on_change=True, path_to_watch="bot.py")#none_stop=True)
