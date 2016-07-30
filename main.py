from telegram.ext import Updater, CommandHandler
import yaml

from handlers import Handlers


def main():
    config = yaml.load(open('config.yml'))
    updater = Updater(config['telegram_token'])

    dp = updater.dispatcher

    handlers = Handlers()

    dp.add_handler(CommandHandler('start', handlers.start_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
