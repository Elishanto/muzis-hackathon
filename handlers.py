from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class Handlers:
    def __init__(self, mongo, config):
        self.db = mongo.parter
        self.config = config

    def start_handler(self, bot, update):
        return bot.sendMessage(update.message.from_user.id, text=self.config['start_message'])

    def create_handler(self, bot, update, args):
        if args:
            name = ' '.join(args)
        else:
            name = str(self.db.playlists.count() + 1)

        buttons = [
            [
                InlineKeyboardButton(text='Длительность плейлиста'),
                InlineKeyboardButton(text='Жанры'),
                InlineKeyboardButton(text='Музыкальная эпоха')
            ]
        ]
        return bot.sendMessage(update.message.from_user.id, text=name, reply_markup=InlineKeyboardMarkup(buttons))
