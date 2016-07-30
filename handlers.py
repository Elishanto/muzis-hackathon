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
            [InlineKeyboardButton(text='Длительность плейлиста', callback_data='0')],
            [InlineKeyboardButton(text='Жанры', callback_data='1')],
            [InlineKeyboardButton(text='Музыкальная эпоха', callback_data='2')]
        ]
        return bot.sendMessage(update.message.from_user.id, text='Playlist "{}"'.format(name),
                               reply_markup=InlineKeyboardMarkup(buttons))
