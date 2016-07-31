from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from utils.api_utils import generate_audio
from utils.handlers_utils import get_playlist_params


class Handlers:
    def __init__(self, mongo, config):
        self.db = mongo.parter
        self.config = config
        self.BUTTONS = [[InlineKeyboardButton(text=x[1], callback_data=x[0])] for x in self.config['names']]

    def start_handler(self, bot, update):
        return bot.sendMessage(update.message.from_user.id, text=self.config['start_message'])

    def get_plst_name(self):
        return 'Плейлист ```{}```:\n'

    def create_handler(self, bot, update, args):
        if args:
            name = ' '.join(args)
        else:
            name = str(self.db.playlists.count() + 1)
        name = '{} #{}'.format(self.get_plst_name().format(name), self.db.playlists.count({'name': name}) + 1)

        self.db.playlists.insert_one({'name': name, 'user_id': update.message.from_user.id})
        self.db.current.update_one({'user_id': update.message.from_user.id},
                                   {'$set': {'name': name}},
                                   upsert=True)

        message = bot.sendMessage(
            update.message.from_user.id,
            text=self.get_plst_name().format(name) + get_playlist_params(self, name),
            reply_markup=InlineKeyboardMarkup(self.BUTTONS),
            parse_mode='markdown')
        self.db.users.update_one(
            {'user_id': update.message.from_user.id},
            {'$set': {'message_id': message.message_id}},
            upsert=True
        )

    def help_handler(self, bot, update):
        return bot.sendMessage(update.message.from_user.id, text=self.config['help_message'])

    def callback_handler(self, bot, update):
        query = update.callback_query
        data = query.data
        name = self.db.current.find_one({'user_id': query.from_user.id})['name']
        bot.answer_callback_query(query.id)
        message_id = self.db.users.find_one({'user_id': query.message.chat.id})['message_id']
        if data == 's':
            bot.editMessageText(
                chat_id=query.message.chat.id,
                message_id=message_id,
                text='Составляю плейлист... \n{}'.format(get_playlist_params(self, name)),
                parse_mode='markdown')
            res, audio_url = generate_audio(self.db, query.from_user.id)

            text = '\n\n'.join([
                                   '\n'.join(['*{}*'.format(x['performer']), x['track_name']]) for x in res
                                   ])
            text += '\n\n' + '_Download_: ' + audio_url
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text=text,
                                       parse_mode='markdown')
        if len(data.split('|')) > 1:
            data = data.split('|')
            to_set = self.config['buttons'][data[0]][data[1]]
            self.db.playlists.update_one({'name': name}, {'$set': {data[0]: to_set}})

            text = self.get_plst_name().format(name) + get_playlist_params(self, name)
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text=text,
                                       reply_markup=InlineKeyboardMarkup(self.BUTTONS),
                                       parse_mode='markdown')
        else:
            buttons = self.config['buttons'][data]
            # if data == 'e':
            #      buttons = [str(y) + '-e' for y in sorted([int(ep.split('-')[0]) for ep in buttons.keys()])]
            #      buttons = [[
            #                     InlineKeyboardButton(
            #                         text=x,
            #                         callback_data='{}|{}'.format(data, x))
            #                 ]
            #                 for x in buttons]
            # else:
            buttons = sorted(buttons.keys())
            buttons = [[InlineKeyboardButton(text=x, callback_data='{}|{}'.format(data, x))]
                           for x in buttons]
            return bot.editMessageText(chat_id=query.message.chat.id,
                                       message_id=message_id,
                                       text=self.get_plst_name().format(name) + get_playlist_params(self, name),
                                       reply_markup=InlineKeyboardMarkup(buttons),
                                       parse_mode='markdown')
