import uuid

from db.database import Session, User, Project
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from sqlalchemy.exc import IntegrityError


SELECTING_ACTION, ADDING_PROJECT, SELECTING_NAME, MAIN = map(chr, range(4))
EDITING, CHANGING_NAME = map(chr, range(4, 6))
SAVE, TYPING = map(chr, range(6, 8))
STOPPING, SHOWING = map(chr, range(8, 10))
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
        InlineKeyboardButton(text='➕Add project', callback_data=str(ADDING_PROJECT)),
        InlineKeyboardButton(text='\U0001F4C1My projects', callback_data=str(SHOWING)),
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    response = {
        "text": "Test",
        "reply_markup": keyboard
    }

    if update.callback_query:
        update.callback_query.answer()
        update.callback_query.edit_message_text(**response)
    else:
        update.message.reply_text(**response)
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

        text = "Your projects"

        buttons = []

        count = projects.count()
        context.user_data["projects"] = projects

        for i in range(0, count, 2):
            row = [
                InlineKeyboardButton(text=projects[i].name, callback_data=str(EDITING)+str(projects[i].name)),
            ]
            if i+1 < count:
                row.append(
                    InlineKeyboardButton(
                        text=projects[i+1].name,
                        callback_data=str(EDITING)+str(projects[i+1].name)
                    )
                )

            buttons.append(row)

        buttons.append([InlineKeyboardButton(text='Return to main', callback_data=str(MAIN))])

        keyboard = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

        return SELECTING_ACTION
    except Exception as e:
        print(str(e))


def edit(update, context):

    error_buttons = [
        [
            InlineKeyboardButton(text="Back to projects list", callback_data=str(END))
        ]
    ]
    error_keyboard = InlineKeyboardMarkup(error_buttons)

    project = {}

    if "current_project" not in context.user_data.keys():

        name = update["callback_query"]["data"][1:]

        for p in context.user_data["projects"]:
            if p.name == name:
                project = p

        if not project:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text="Error occurred",
                reply_markup=error_keyboard
            )

        context.user_data["current_project"] = project
    else:
        project = context.user_data["current_project"]

    buttons = [
        [
            InlineKeyboardButton(text="Change name", callback_data=str(CHANGING_NAME)),
        ],
        [
            InlineKeyboardButton(text="Back to projects list", callback_data=str(SHOWING))
        ]
    ]

    text = "<b>Name:</b> {}\n" \
           "<b>Token:</b> {}\n".format(project.name, project.token)

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    return EDITING


def change_name(update, context):
    update.callback_query.answer()
    update.callback_query.edit_message_text("Enter new name")

    return SELECTING_NAME


def edit_name(update, context):
    new_name = update.message.text
    context.user_data["new_name"] = new_name

    buttons = [
        [
            InlineKeyboardButton(text="Yes", callback_data=str(SAVE)),
            InlineKeyboardButton(text="No", callback_data=str(EDITING)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    text = "Save?"

    update.message.reply_text(text=text, reply_markup=keyboard)
    return SELECTING_NAME


def save(update, context):
    session = Session()

    new_name = context.user_data["new_name"]
    project = context.user_data["current_project"]

    session.query(Project).filter(Project.id == project.id).update({"name": new_name})
    session.commit()

    project.name = new_name
    context.user_data["current_project"] = project

    return edit(update, context)


edit_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit, pattern='^' + str(EDITING) + "*")],
    states={
        EDITING: [
            CallbackQueryHandler(change_name, pattern="^" + str(CHANGING_NAME) + "$"),
            CallbackQueryHandler(edit, pattern='^' + str(EDITING) + '*'),
        ],
        SELECTING_NAME: [
            MessageHandler(Filters.text, edit_name),
            CallbackQueryHandler(save, pattern="^" + str(SAVE) + "$")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(show_projects, pattern="^" + str(SHOWING) + "$"),
        CallbackQueryHandler(edit, pattern="^" + str(EDITING) + "$"),
    ],
    map_to_parent={
        END: SELECTING_ACTION,
    }
)

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', main),
    ],
    allow_reentry=True,
    states={
        SELECTING_ACTION: [
            CommandHandler("menu", main),
            CallbackQueryHandler(main, pattern='^' + str(MAIN) + '$'),
            CallbackQueryHandler(register, pattern='^' + str(ADDING_PROJECT) + '$'),
            CallbackQueryHandler(show_projects, pattern='^' + str(SHOWING) + '$'),
            edit_handler
        ],
        TYPING: [MessageHandler(Filters.text, typing_name)]

    },

    fallbacks=[
        CommandHandler('stop', stop),
    ],
)
