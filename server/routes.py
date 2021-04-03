# -*- coding: utf-8 -*-
from db.database import Session, Project
from flask import request, jsonify


def init_routes(app, bot=None):
    """
    {
        token: str,
        message: {
            type: str,
            content: str
        }
    }
    """

    @app.route("/new_log", methods=["POST"])
    def new_message():

        def format_text(project_name, message):

            cases = {
                "error":
                    "\u26D4New error from %s:\n"
                    "%s",
                "warning":
                    "⚠️New warning from %s:\n"
                    "%s",
                "log":
                    "\U0001F4ACNew log from %s:\n"
                    "%s",
            }

            return cases[message["type"]] % (project_name, log["message"]["content"])

        log = request.json

        session = Session()
        project = session.query(Project).filter_by(token=log["token"]).first()
        if not project:
            return {
                "ok": False,
                "error": "Project not found! Please check your token"
            }

        text = format_text(project.name, log["message"])

        bot.sendMessage(chat_id=project.user_id, text=text)
        return jsonify({"ok": True})
