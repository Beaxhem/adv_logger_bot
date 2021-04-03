import os

from server import Server
from bot import Bot


TOKEN = os.environ["TOKEN"]


class Logger:
    def __init__(self, bot, server):

        self.bot = bot
        self.server = server

    def run(self):
        self.bot.run()
        self.server.run()


b = Bot(token=TOKEN)
b.run()
s = Server(b.get_bot())
s.run()
#
# log = Logger(b, s)
# log.run()

