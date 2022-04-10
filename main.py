import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import sqlite3

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5110951414:AAF17EXuVIoLbUcDzieFwTF-WqwGtfQD1dM'
CLUBS = {}


def menu(update, context):
    reply_keyboard = [['/info', '/booking'], ['/check_booking']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Выберите команду, интересующую вас.", reply_markup=markup)


def start(update, context):
    reply_keyboard = [['/info', '/booking'], ['/check_booking']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Привет! Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе! "
                              "Выберите команду, интересующую вас.", reply_markup=markup)


def choose_club(update, context):
    clubs = [[x] for x in CLUBS.keys()]
    clubs.append(['/menu'])
    markup_clubs = ReplyKeyboardMarkup(clubs, one_time_keyboard=False)
    update.message.reply_text('Выберите компьютерный клуб, в котором хотите сделать бронирование:',
                              reply_markup=markup_clubs)
    return 1


def choose_hall(update, context):
    context.user_data['club'] = update.message.text
    halls = [[x] for x in CLUBS[context.user_data['club']]]
    halls.append(['/menu'])

    markup_halls = ReplyKeyboardMarkup(halls, one_time_keyboard=False)
    update.message.reply_text(f'Какой зал в клубе {context.user_data["club"]} вам нужен?', reply_markup=markup_halls)
    return 2


def choose_seats(update, context):
    context.user_data['hall'] = update.message.text
    update.message.reply_text(f'Сколько мест в зале {context.user_data["hall"]} вам нужно?',
                              reply_markup=ReplyKeyboardRemove())
    return 3


def choose_date(update, context):
    context.user_data['seats'] = update.message.text
    update.message.reply_text(f"Введите дату в формате <dd.mm.yy>:")
    return 4


def choose_time(update, context):
    context.user_data['date'] = update.message.text
    update.message.reply_text("Введите начальное время в формате <HH:MM>:")
    return 5


def choose_duration(update, context):
    context.user_data['time'] = update.message.text
    update.message.reply_text("Введите продолжительность бронирования в часах (число):")
    return 6


def check_booking(update, context):
    context.user_data['duration'] = update.message.text
    # Здесь буду проверять, есть ли свободные пк на данный момент
    update.message.reply_text("Проверка наличия компьютеров на это время...")
    if True:
        update.message.reply_text(f"Все отлично!")
        # Здесь будет высчитываться сумма бронирования на основе данных из БД
        sum_of_booking = 1400
        yes_and_no = [['Yes'], ['No'], ['/menu']]
        markup_yes_and_no = ReplyKeyboardMarkup(yes_and_no, one_time_keyboard=False)
        update.message.reply_text(f"Сумма бронирования составляет {sum_of_booking} рублей. Подтверждаете?",
                                  reply_markup=markup_yes_and_no)
    else:
        update.message.reply_text("К сожалению, свободных ПК нет на это время(")

    return 7


def print_result(update, context):
    if update.message.text == 'Yes':
        update.message.reply_text('Успешное бронирование!', reply_markup=ReplyKeyboardRemove())
        menu(update, context)
    else:
        update.message.reply_text('Неудачно', reply_markup=ReplyKeyboardRemove())
        menu(update, context)
    context.user_data.clear()


def load_info_of_clubs():
    with sqlite3.connect('YandexProject.sqlite') as con:
        cur = con.cursor()
        clubs = list(map(lambda x: x[0], cur.execute(f"""SELECT title FROM Clubs """).fetchall()))

        for club in clubs:
            halls = cur.execute(f"""SELECT VIP FROM Halls WHERE ClubId = (SELECT ClubId FROM Clubs 
            WHERE title = '{club}')""").fetchall()
            CLUBS[club] = {}
            for hall in halls:
                info_of_hall = cur.execute(f"""SELECT seats, price, specifications FROM Halls 
                WHERE VIP = '{hall[0]}' AND ClubId = (SELECT ClubId FROM Clubs WHERE title = '{club}')""").fetchall()

                seats = info_of_hall[0][0]
                price = info_of_hall[0][1]
                specifications = info_of_hall[0][2]
                CLUBS[club][hall[0]] = {'price': price, 'seats': seats, 'specifications': specifications}


def print_names_clubs(update, context):
    clubs = [[x] for x in CLUBS.keys()]
    clubs.append(['/menu'])
    markup_clubs = ReplyKeyboardMarkup(clubs, one_time_keyboard=False)
    num_of_clubs = len(clubs) - 1

    if num_of_clubs == 1:
        reply_text = f"Всего у нас {num_of_clubs} клуб. "
    elif num_of_clubs in [2, 3, 4]:
        reply_text = f"Всего у нас {num_of_clubs} клуба. "
    else:
        reply_text = f"Всего у нас {num_of_clubs} клубов. "
    reply_text += 'Выберите нужный'

    update.message.reply_text(reply_text, reply_markup=markup_clubs)
    return 1


def print_info_about_club(update, context):
    club = update.message.text
    halls = CLUBS[club]
    if len(halls) == 1:
        reply_text = f"В клубе {club} {len(halls)} зал.\n"
    else:
        reply_text = f"В клубе {club} {len(halls)} зала.\n"
    for hall in halls:
        # Указываем места в соответствии с числом
        if str(CLUBS[club][hall]['seats'])[-1] == '1' and str(CLUBS[club][hall]['seats'])[-2:] != '11':
            reply_text += f"{hall.capitalize()} - {CLUBS[club][hall]['seats']} место, "
        elif str(CLUBS[club][hall]['seats'])[-1] in ['2', '3', '4'] \
                and str(CLUBS[club][hall]['seats'])[-2:] not in [12, 13, 14]:
            reply_text += f"{hall.capitalize()} - {CLUBS[club][hall]['seats']} места, "
        else:
            reply_text += f"{hall.capitalize()} - {CLUBS[club][hall]['seats']} мест, "

        # Указываем цену в соответствии с числом
        if str(CLUBS[club][hall]['price'])[-1] == '1' and str(CLUBS[club][hall]['price'])[-2:] != '11':
            reply_text += f"{CLUBS[club][hall]['price']} рубль/час. "
        elif str(CLUBS[club][hall]['price'])[-1] in ['2', '3', '4'] \
                and str(CLUBS[club][hall]['price'])[-2:] not in [12, 13, 14]:
            reply_text += f"{CLUBS[club][hall]['price']} рубля/час. "
        else:
            reply_text += f"{CLUBS[club][hall]['price']} рублей/час. "
        reply_text += f"Характеристики: {CLUBS[club][hall]['specifications']}.\n"

    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
    menu(update, context)
    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text('Всего доброго!')
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text("Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе!")


def close_keyboard(update, context):
    update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())


def main():
    updater = Updater(TOKEN)
    load_info_of_clubs()
    dp = updater.dispatcher

    conv_handler_booking = ConversationHandler(
        entry_points=[CommandHandler('booking', choose_club)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, choose_hall)],
            2: [MessageHandler(Filters.text & ~Filters.command, choose_seats)],
            3: [MessageHandler(Filters.text & ~Filters.command, choose_date)],
            4: [MessageHandler(Filters.text & ~Filters.command, choose_time)],
            5: [MessageHandler(Filters.text & ~Filters.command, choose_duration)],
            6: [MessageHandler(Filters.text & ~Filters.command, check_booking)],
            7: [MessageHandler(Filters.text & ~Filters.command, print_result)]
        },
        fallbacks=[CommandHandler('stop', stop)])

    conv_handler_info = ConversationHandler(
        entry_points=[CommandHandler('info', print_names_clubs)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, print_info_about_club)],
        },
        fallbacks=[CommandHandler('stop', stop)])

    dp.add_handler(conv_handler_booking)
    dp.add_handler(conv_handler_info)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('booking', choose_club))
    dp.add_handler(CommandHandler('menu', menu))
    dp.add_handler(CommandHandler('info', print_names_clubs))
    dp.add_handler(CommandHandler('close', close_keyboard))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
