import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import sqlite3
from datetime import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
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
    update.message.reply_text('Выберите компьютерный клуб, в котором хотите сделать бронирование',
                              reply_markup=markup_clubs)
    return 1


def choose_hall(update, context):
    if update.message.text not in CLUBS:
        choose_club(update, context)
    else:
        context.user_data['club'] = update.message.text
        halls = [[x] for x in CLUBS[context.user_data['club']]]
        halls.append(['/menu'])

        markup_halls = ReplyKeyboardMarkup(halls, one_time_keyboard=False)
        update.message.reply_text(f'Какой зал в клубе {context.user_data["club"]} вам нужен?',
                                  reply_markup=markup_halls)
        return 2


def choose_seats(update, context):
    # if update.message.text not in CLUBS[context.user_data['club']]:
    #     choose_hall(update, context)
    #     print(update.message.text)
    # print(update.message.text)
    context.user_data['hall'] = update.message.text
    button_to_menu = ReplyKeyboardMarkup([['/menu']], one_time_keyboard=False)
    update.message.reply_text(f'Сколько мест в зале {context.user_data["hall"]} вам нужно?',
                              reply_markup=button_to_menu)
    return 3


def choose_date(update, context):
    # if type(update.message.text) is not int:
    #     while True:
    #         update.message.reply_text('Введите число!')
    #         if type(update.message.text) is int:
    #             break
    context.user_data['seats'] = update.message.text
    button_to_menu = ReplyKeyboardMarkup([['/menu']], one_time_keyboard=False)
    update.message.reply_text(f"Введите дату в формате <dd.mm.yy>:", reply_markup=button_to_menu)
    return 4


def choose_time(update, context):
    context.user_data['date'] = update.message.text
    button_to_menu = ReplyKeyboardMarkup([['/menu']], one_time_keyboard=False)
    update.message.reply_text("Введите начальное время в формате <HH:MM>:", reply_markup=button_to_menu)
    return 5


def choose_duration(update, context):
    context.user_data['time'] = update.message.text
    button_to_menu = ReplyKeyboardMarkup([['/menu']], one_time_keyboard=False)
    update.message.reply_text("Введите продолжительность бронирования в часах (число):", reply_markup=button_to_menu)
    return 6


def check_booking(update, context):
    context.user_data['duration'] = update.message.text
    flag_booking_complete = False
    free_computers = []
    # try:
    with sqlite3.connect('YandexProject.sqlite') as con:
        cur = con.cursor()
        hall = context.user_data['hall']
        club = context.user_data['club']
        print(hall, club)
        club_id = cur.execute(f"""SELECT clubid FROM clubs WHERE title = '{club}'""").fetchone()[0]
        price0 = cur.execute(f"""SELECT price FROM halls WHERE vip = '{hall}' AND clubid = {club_id}""").fetchone()
        # price = int(price0)
        print(price0)
        full_price = price0 * int(context.user_data['duration']) * int(context.user_data['seats'])

        update.message.reply_text("Проверка наличия компьютеров на это время...")

        halls0 = cur.execute(f"""SELECT computerid FROM computers WHERE hallid =
                            (SELECT hallid FROM halls WHERE vip = '{context.user_data['hall']}' AND clubid =
                            (SELECT clubid FROM clubs WHERE title = '{context.user_data['club']}'))""").fetchall()
        seats = list(map(lambda x: x[1:-2], list(map(str, halls0))))

        for i in range(len(seats)):
            id = seats[i]
            if can_booking(context.user_data['date'], context.user_data['time'], context.user_data['duration'], id):
                free_computers.append(id)


        # if True:
        #     update.message.reply_text(f"Все отлично!")
        #     # Здесь будет высчитываться сумма бронирования на основе данных из БД
        #
        #     yes_and_no = [['Да'], ['Нет'], ['/menu']]
        #     markup_yes_and_no = ReplyKeyboardMarkup(yes_and_no, one_time_keyboard=False)
        #     update.message.reply_text(f"Сумма бронирования составляет {full_price} рублей. Подтверждаете?",
        #                               reply_markup=markup_yes_and_no)
        # else:
        #     update.message.reply_text("К сожалению, свободных ПК нет на это время(")

    # except Exception:
    #     update.message.reply_text('Неправильно введены данные. Повторите попытку')
    #     stop_to_menu(update, context)

    return 7


def print_result(update, context):
    if update.message.text == 'Да':
        update.message.reply_text('Успешное бронирование!', reply_markup=ReplyKeyboardRemove())
        stop_to_menu(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_text('Неудачно', reply_markup=ReplyKeyboardRemove())
        stop_to_menu(update, context)
    context.user_data.clear()


def can_booking(date, time_start, duration, computer):
    flag_can_booking = True
    time_finish = str(int(time_start.split(':')[0]) + duration) + ':' + time_start.split(':')[1]
    print(time_finish)
    with sqlite3.connect('YandexProject.sqlite') as con:
        cur = con.cursor()
        bookings = cur.execute(f"""SELECT * FROM Booking WHERE ComputerId = {computer}
        AND date = '{date}'""").fetchall()
        for booking in bookings:
            if check_time(time_start, time_finish, booking[4], booking[5]):
                flag_can_booking = False
    if flag_can_booking:
        return True
    return False


def check_time(t0_self, t1_self, t0_other, t1_other):
    time_start = tuple([int(t0_self.split(':')[0]), int(t0_self.split(':')[1])])
    time_finish = tuple([int(t1_self.split(':')[0]), int(t1_self.split(':')[1])])
    time_start_other = tuple([int(t0_other.split(':')[0]), int(t0_other.split(':')[1])])
    time_finish_other = tuple([int(t1_other.split(':')[0]), int(t1_other.split(':')[1])])

    time_start = time(time_start[0], time_start[1])
    time_finish = time(time_finish[0], time_finish[1])
    time_start_other = time(time_start_other[0], time_start_other[1])
    time_finish_other = time(time_finish_other[0], time_finish_other[1])

    if (time_start_other < time_start < time_finish_other \
        or time_start_other < time_finish < time_finish_other) \
            or (time_start <= time_start_other and time_finish >= time_finish_other) \
            or (time_start >= time_start_other and time_finish <= time_finish_other):
        return True
    return False


def booking_sqlite():
    pass


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


def stop_to_menu(update, context):
    menu(update, context)
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
        fallbacks=[CommandHandler('menu', stop_to_menu)])

    conv_handler_info = ConversationHandler(
        entry_points=[CommandHandler('info', print_names_clubs)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, print_info_about_club)],
        },
        fallbacks=[CommandHandler('menu', menu)])

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
