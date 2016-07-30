class Handlers:
    def __init__(self):
        pass

    def start_handler(self, bot, update):
        return bot.sendMessage(update.message.from_user.id, text='Hello!')
