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

        if self.db.playlists.find({'name': name}):
            name = '{} #{}'.format(name, self.db.playlists.count({'name': name}) + 1)

        self.db.playlists.insert_one({'name': name, 'user_id': update.message.from_user.id})
        self.db.current.update_one({'user_id': update.message.from_user.id}, {'$set': {'name': name}}, upsert=True)

        buttons = [
            [InlineKeyboardButton(text='Длительность плейлиста', callback_data='0')],
            [InlineKeyboardButton(text='Жанры', callback_data='1')],
            [InlineKeyboardButton(text='Музыкальная эпоха', callback_data='2')],
            [InlineKeyboardButton(text='Тематика', callback_data='3')]
        ]
        return bot.sendMessage(update.message.from_user.id, text='Playlist "{}"'.format(name),
                               reply_markup=InlineKeyboardMarkup(buttons))

    def callback_handler(self, bot, update):
        query = update.callback_query
        data = query.data
        name = self.db.current.find_one({'user_id': query.from_user.id})['name']
        bot.answer_callback_query(query.id)
        if len(data.split('|')) > 1:
            data = data.split('|')
            self.db.playlists.update_one({'name': name}, {'$set': {data[0]: data[1]}})
        else:
            button = list(self.config['buttons'].keys())[int(data)]
            buttons = self.config['buttons'][button]

            buttons = [[InlineKeyboardButton(text=x, callback_data='{}|{}'.format(data, x))]
                       for x in buttons]
            return bot.sendMessage(chat_id=query.message.chat.id, text='Playlist "{}"'.format(name), reply_markup=InlineKeyboardMarkup(buttons))
