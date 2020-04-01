from telegram.ext import Updater
from bot.handlers import conv_handler


class Bot:

    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.init_handlers()

    def init_handlers(self):

        self.dispatcher.add_handler(conv_handler)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def get_bot(self):
        return self.updater.bot

