import yaml

from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler

from handlers import Handlers


def main():
    config = yaml.load(open('config.yml'))
    updater = Updater(config['telegram_token'])

    dp = updater.dispatcher

    handlers = Handlers(MongoClient())

    dp.add_handler(CommandHandler('start', handlers.start_handler))
    dp.add_handler(CommandHandler('create', handlers.create_handler, pass_args=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
