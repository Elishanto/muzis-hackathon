import logging
from collections import OrderedDict

import yaml
import os

from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from handlers import Handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    config = yaml.load(open('config.yml', encoding='utf-8'))
    updater = Updater(
        config['telegram_token'] if not os.environ.get('telegram_token') else os.environ.get('telegram_token')
    )

    dp = updater.dispatcher

    handlers = Handlers(MongoClient(), config)

    dp.add_handler(CommandHandler('start', handlers.start_handler))
    dp.add_handler(CommandHandler('create', handlers.create_handler, pass_args=True))
    dp.add_handler(CallbackQueryHandler(handlers.callback_handler))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
