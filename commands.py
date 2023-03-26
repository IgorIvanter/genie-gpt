import config
import telegram
import openai
from telegram.ext import CommandHandler
from config import WELCOME_MESSAGE

logging = config.logging


def handle_command_start(update, context):
    """Start the bot"""
    update.message.reply_text(text=WELCOME_MESSAGE,
                              parse_mode=telegram.ParseMode.MARKDOWN)


# define a function to raise errors
def handle_command_error(update, context):
    """a special command for debugging, raises an EnvironmentError"""
    raise EnvironmentError


def handle_command_timeout(update, context):
    raise openai.error.Timeout


def handle_command_reset(update, context):
    """reset the conversation history"""
    logging.debug("Entered handle_command_reset()")
    logging.debug("History before clearing:")
    logging.debug(context.user_data["messages"])
    context.user_data["messages"] = [context.user_data["messages"][0]]
    logging.debug("History after clearing:")
    logging.debug(context.user_data["messages"])
    update.message.reply_text("Perfect!\n\nOur conversation history has been cleared for me.\n\nAnything above this message is out of my memory now😁\n\nNow, what can I help you with?")


def handle_command_help(update, context):
    """Get the list of all commands available"""
    logging.debug("Entering help_command")
    # Get the list of registered command handlers from the dispatcher
    logging.debug("Printing all handlers:")
    logging.debug(context.dispatcher.handlers[0])
    handlers = context.dispatcher.handlers[0]
    command_handlers = [handler for handler in handlers if isinstance(handler, CommandHandler)]
    logging.debug("Printing command handlers:")
    logging.debug(command_handlers)
    commands = [command_handler.command for command_handler in command_handlers]
    logging.debug("Printing commands:")
    logging.debug(commands)
    help_msg = f'*Here is the list of available commands:*\n\n'

    for command_handler in command_handlers:
        for command in command_handler.command:
            help_msg += f"/{command} - {command_handler.callback.__doc__ or 'no description 🙁'}\n\n"

    # Send the help message to the user
    logging.debug(f"Constructed help message")
    logging.debug(help_msg)
    update.message.reply_text(text=help_msg, parse_mode=telegram.ParseMode.MARKDOWN)
    logging.debug("Exiting help command")

