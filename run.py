from server import Server
from bot import Bot


class Logger:
    def __init__(self, bot, server):

        self.bot = bot
        self.server = server

    def run(self):
        self.bot.run()
        self.server.run()


b = Bot(token="991842513:AAG98klfgnMa8KcE2iEoKFVmIYqmtFgqhC8")
b.run()
s = Server(b.get_bot())
s.run()
#
# log = Logger(b, s)
# log.run()

