from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.api_utils import generate_audio

BUTTONS = [
    [InlineKeyboardButton(text='Длительность плейлиста', callback_data='l')],
    [InlineKeyboardButton(text='Жанры', callback_data='g')],
    [InlineKeyboardButton(text='Музыкальная эпоха', callback_data='e')],
    [InlineKeyboardButton(text='Тематика', callback_data='t')],
    [InlineKeyboardButton(text='=Сохранить=', callback_data='s')]
]


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
            name = '"{}" #{}'.format(name, self.db.playlists.count({'name': name}) + 1)

        self.db.playlists.insert_one({'name': name, 'user_id': update.message.from_user.id})
        self.db.current.update_one({'user_id': update.message.from_user.id}, {'$set': {'name': name}}, upsert=True)

        message = bot.sendMessage(update.message.from_user.id, text='Playlist {}'.format(name),
                                  reply_markup=InlineKeyboardMarkup(BUTTONS))
        self.db.users.update_one(
            {'user_id': update.message.from_user.id},
            {'$set': {'message_id': message.message_id}},
            upsert=True
        )

    def callback_handler(self, bot, update):
        query = update.callback_query
        data = query.data
        name = self.db.current.find_one({'user_id': query.from_user.id})['name']
        bot.answer_callback_query(query.id)
        message_id = self.db.users.find_one({'user_id': query.message.chat.id})['message_id']
        if data == 's':
            bot.editMessageText(chat_id=query.message.chat.id,
                                message_id=message_id,
                                text='Составляю плейлист...')
            playlist = generate_audio(self.db, query.from_user.id)
            text = '\n'.join(['{} - {}'.format(x['performer'], x['track_name']) for x in playlist[0]])
            text += '\n' + playlist[1]
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text=text)
        if len(data.split('|')) > 1:
            data = data.split('|')
            self.db.playlists.update_one({'name': name}, {'$set': {data[0]: self.config['buttons'][data[0]][data[1]]}})
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text='Playlist "{}"'.format(name),
                                       reply_markup=InlineKeyboardMarkup(BUTTONS))
        else:
            buttons = self.config['buttons'][data]

            buttons = [[InlineKeyboardButton(text=x, callback_data='{}|{}'.format(data, x))]
                       for x in buttons]
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text='Playlist "{}"'.format(name),
                                       reply_markup=InlineKeyboardMarkup(buttons))
