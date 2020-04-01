import uuid

from db.database import Session, User, Project
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import  CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from sqlalchemy.exc import IntegrityError


SELECTING_ACTION, ADDING_PROJECT, SELECTING_NAME, MAIN = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, SHOWING = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END


def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END


def start(update, context):
    session = Session()

    try:
        u = User(chat_id=update.message.chat.id)

        session.add(u)
        session.commit()

    except IntegrityError:
        print("User already exists")

    buttons = [[
        InlineKeyboardButton(text='To main menu', callback_data=str(MAIN)),
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text("Choose the menu", reply_markup=keyboard)
    return SELECTING_ACTION


def main(update, context):
    buttons = [[
        InlineKeyboardButton(text='Add project', callback_data=str(ADDING_PROJECT)),
        InlineKeyboardButton(text='My projects', callback_data=str(SHOWING)),
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=update.effective_chat.id, reply_markup=keyboard)
    else:
        update.message.reply_text(text=update.effective_chat.id, reply_markup=keyboard)
    return SELECTING_ACTION


def register(update, context):
    update.callback_query.answer()
    update.callback_query.edit_message_text(text="Enter the name of your project")

    return TYPING


def typing_name(update, context):

    try:
        session = Session()

        token = uuid.uuid1()
        project = Project(token=token, name=update.message.text, user_id=update.message.chat.id)
        session.add(project)
        session.commit()

        update.message.reply_text(text=str(token))

        return main(update, context)

    except Exception as e:
        print(str(e))


def show_projects(update, context):
    chat_id = update.callback_query.message.chat.id
    try:
        session = Session()

        projects = session.query(Project).filter_by(user_id=chat_id)

        text = ""

        for i, project in enumerate(projects):
            text += "%s. %s\n" % (i + 1, project.name)
        if not text:
            text = "No projects yet"

        buttons = [
            [
                InlineKeyboardButton(text='Return to main', callback_data=str(MAIN)),
            ]
        ]

        keyboard = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        return SELECTING_ACTION
    except Exception as e:
        print(str(e))


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        SELECTING_ACTION: [
            CallbackQueryHandler(main, pattern='^' + str(MAIN) + '$'),
            CallbackQueryHandler(register, pattern='^' + str(ADDING_PROJECT) + '$'),
            CallbackQueryHandler(show_projects, pattern='^' + str(SHOWING) + '$'),
        ],
        TYPING: [MessageHandler(Filters.text, typing_name)]

    },

    fallbacks=[
        CommandHandler('stop', stop),
    ],
)
