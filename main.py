from telegram.ext import Updater, CommandHandler
import yaml


def main():
    config = yaml.load(open('config.yml'))
    updater = Updater(config['telegram_token'])

    dp = updater.dispatcher


if __name__ == '__main__':
    main()
