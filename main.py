from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
import telegram
import openai
from moviepy.editor import AudioFileClip
from dotenv import load_dotenv
import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


load_dotenv()  # Load environment variables from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

messages = [{"role": "system", "content": "You are SuperTelegramGPT, a helpful telegram bot who is also extremely funny and a very cocky, and likes to troll people a bit and show character, but you still remain very helpful and you strive to fulfill all user's requests. You are a powerful creature with ears so you can hear if a user sends you a telegram voice note."}]


# Define the callback functions for the buttons
def button1_callback(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You pressed button 1")


def button2_callback(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You pressed button 2")


def button_click_handler(update, context):
    query = update.callback_query
    query.answer()
    button_id = query.data
    
    if button_id == 'button1':
        button1_callback(update, context)
    elif button_id == 'button2':
        button2_callback(update, context)
    else:
        query.edit_message_text(text="Invalid button")


def buttons_demo(update, context):
    # Create the inline keyboard with a button
    inline_keyboard = [[InlineKeyboardButton('Button 1', callback_data='button1'), InlineKeyboardButton('Button 2', callback_data='button2')]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    # Add the keyboard to the message
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    update.message.reply_text('Press a button:', reply_markup=reply_markup)


def text_message(update, context):
    messages.append({"role": "user", "content": update.message.text})
    chat_message = update.message.reply_text(text='Working on it... ⏳')
    # Send typing action
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        timeout=30
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=chat_message.message_id)
    update.message.reply_text(text=f"*[Bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    messages = messages[-10:]


def voice_message(update, context):
    voice_received_message = update.message.reply_text("I've received a voice message! Please give me a second to respond ⏳")
    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file.download("voice_message.ogg")
    audio_clip = AudioFileClip("voice_message.ogg")
    audio_clip.write_audiofile("voice_message.mp3")
    audio_file = open("voice_message.mp3", "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file).text
    inline_keyboard = [[InlineKeyboardButton('Edit', callback_data='button1'), InlineKeyboardButton('Submit', callback_data='button2')]]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=voice_received_message.message_id)
    update.message.reply_text(text=f"*[You]:* _{transcript}_", parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
    chat_message = update.message.reply_text(text='Working on it... ⏳')
    messages.append({"role": "user", "content": transcript})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    context.bot.delete_message(chat_id=update.message.chat_id, message_id=chat_message.message_id)
    update.message.reply_text(text=f"*[Bot]:* {ChatGPT_reply}", parse_mode=telegram.ParseMode.MARKDOWN)
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    messages = messages[-10:]


def start(update, context):
    update.message.reply_text(text="*Welcome to GenieGPT!*\n\n*Who am I?*\n\nI am GenieGPT - a powerful AI system, I analyze your message and provide you with a helpful response as quickly as possible. You can also send me voice notes and I will hear you (yeah I have ears 😱)\n\n*What can I do?*\n\nFrom writing essays on classic literature to explaining quantum field theory - you name it. Just type in your question and I will get back to you ASAP 😎\n\n*Limitations*\n\nPlease keep in mind that sometimes I may not answer because I am overloaded with requests from other users.", parse_mode=telegram.ParseMode.MARKDOWN)

# define a function to handle errors
def error_handler(update, context):
    logger.error(msg="Exception occurred: %s", exc_info=context.error)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Sorry, an error occurred: '{str(context.error)}'. If it's something strange please contact @igor_ivanter for questions.")


updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('buttons', buttons_demo))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', start))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), text_message))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
# add the error handler to dispatcher
dispatcher.add_error_handler(error_handler)
dispatcher.add_handler(CallbackQueryHandler(button_click_handler))
updater.start_polling()
updater.idle()