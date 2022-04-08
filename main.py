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


def start(update, context):
    reply_keyboard = [['/info', '/booking'], ['/check_booking']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Привет! Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе! "
                              "Выберите команду, интересующую вас.", reply_markup=markup)
    return 1


def choose_club(update, context):
    clubs = [['Шокс'], ['Лимбо'], ['Геймбар'], ['Игромания'], ['/menu']]
    markup_clubs = ReplyKeyboardMarkup(clubs, one_time_keyboard=False)
    update.message.reply_text('Выберите компьютерный клуб, в котором хотите сделать бронирование:',
                              reply_markup=markup_clubs)
    return 1


def choose_hall(update, context):
    context.user_data['club'] = update.message.text
    halls = [['VIP'], ['обычный'], ['/cancel'], ['/menu']]
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
        start(update, context)
    else:
        update.message.reply_text('Неудачно', reply_markup=ReplyKeyboardRemove())
        start(update, context)
    context.user_data.clear()


def stop(update, context):
    update.message.reply_text('Всего доброго!')
    return ConversationHandler.END


def menu(update, context):
    context.user_data.clear()
    start(update, context)
    # Здесь будет возврат в меню


def help(update, context):
    update.message.reply_text("Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе!")


def close_keyboard(update, context):
    update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
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

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('booking', choose_club))
    dp.add_handler(CommandHandler('menu', menu))
    dp.add_handler(CommandHandler('close', close_keyboard))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
