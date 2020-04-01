from flask import Flask
from server.routes import init_routes


class Server:

    def __init__(self, bot, app=Flask(__name__)):
        self.bot = bot
        self.app = app
        init_routes(self.app, self.bot)

    def run(self):
        self.app.run(host="0.0.0.0")
