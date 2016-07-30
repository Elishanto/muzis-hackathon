class Handlers:
    def __init__(self, mongo):
        self.db = mongo.parter

    def start_handler(self, bot, update):
        return bot.sendMessage(update.message.from_user.id, text='Hello!')

    def create_handler(self, bot, update, args):
        if args:
            name = ' '.join(args)
        else:
            name = str(self.db.playlists.count()+1)

        return bot.sendMessage(update.message.from_user.id, text=name)
