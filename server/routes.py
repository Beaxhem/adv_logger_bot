from db.database import Session


def init_routes(app, bot=None):
    @app.route("/")
    def start():
        bot.sendMessage(chat_id=370025629, text="Hello")
        return "Hello world""Hello world"
