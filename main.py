import logging
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5110951414:AAF17EXuVIoLbUcDzieFwTF-WqwGtfQD1dM'

reply_keyboard = [['/info', '/booking'], ['/check_booking']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


def start(update, context):
    update.message.reply_text("Привет! Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе! "
                              "Выберите команду, интересующую вас.", reply_markup=markup)
    return 1


def choose_club(update, context):
    clubs = [['Здесь'], ['будут'], ['клубы'], ['из БД'], ['Назад']]
    markup_clubs = ReplyKeyboardMarkup(clubs, one_time_keyboard=False)
    update.message.reply_text('Выберите компьютерный клуб, в котором хотите сделать бронирование:',
                              reply_markup=markup_clubs)
    return 1


def choose_hall(update, context):
    context.user_data['club'] = update.message.text
    halls = [['VIP'], ['Обычный'], ['Назад']]
    markup_halls = ReplyKeyboardMarkup(halls, one_time_keyboard=False)
    update.message.reply_text(f'Какой зал в клубе {context.user_data["club"]} вам нужен?', reply_markup=markup_halls)
    return 2


def choose_seats(update, context):
    context.user_data['hall'] = update.message.text
    update.message.reply_text(f"Сколько мест в зале '{context.user_data['hall']}' вам нужно?")
    return 3


def check_booking(update, context):
    # Здесь буду проверять, есть ли свободные пк на данный момент
    context.user_data['seats'] = update.message.text
    update.message.reply_text(str(context.user_data))
    context.user_data.clear()

    return ConversationHandler.END


def stop(update, context):
    update.message.reply_text('Всего доброго!')
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text("Я бот Игорь, созданный для бронирования компьютеров в компьютерном клубе!")


def close_keyboard(update, context):
    update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('booking', choose_club)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, choose_hall)],
            2: [MessageHandler(Filters.text & ~Filters.command, choose_seats)],
            3: [MessageHandler(Filters.text & ~Filters.command, check_booking)]
        },
        fallbacks=[CommandHandler('stop', stop)])

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('booking', choose_club))
    dp.add_handler(CommandHandler('close', close_keyboard))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
