# -*- coding: utf-8 -*-
import os
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, RegexHandler, ConversationHandler, CommandHandler, MessageHandler, Filters 
import s_list
# import some_api_lib
# import ...

# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
some_api_token = os.environ['SOME_API_TOKEN']
#             ...


#       Your bot code below
# bot = telebot.TeleBot(token)
# some_api = some_api_lib.connect(some_api_token)
#              ...

list_of_stuff = s_list.ListOfStuff()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

NAME, OBJECTS = range(2)
HELP = 0

#every callback must feature bot and update as positional arguments
def start(bot,update):
    update.message.reply_text('Hi, my name is PlutoneBot. I will help you make a list of stuff you need. '
    'Send /cancel to stop talking to me. '
    'Now, tell me the name of the one that\'s gonna bring the object you want to add to the list')
    return NAME #each callback must return the next state

def name(bot, update):
    list_of_stuff.setKey(update.message.text)
    update.message.reply_text('Nice, now write the object you wish to add..')
    return OBJECTS

def ogg(bot, update):
    list_of_stuff.setValue(update.message.text)
    update.message.reply_text('Now, use the /start command if you want to keep adding items, or /print command to print the list')
    return ConversationHandler.END

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye, I hope we can talk again someday')
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def print_stuff(bot,update):
    reply = ''
    for k,v in list_of_stuff.getDict().items():
        reply += k + ': '
        for index in range(len(v)):
            reply += v[index] + ' '
        reply += '\n' 

    update.message.reply_text(reply)

def help(bot, update):
    custom_keyboard = [['Commands'],['Source code'], ['Done']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text="Custom Keyboard Test", reply_markup=reply_markup)
    return HELP

def helper(bot, update):
    if update.message.text == 'Commands':
        update.message.reply_text("""/start: use start command to begin adding items to the list\n
        /print: prints the list of items with the owners""")
    elif update.message.text == 'Source code':
        update.message.reply_text('https://github.com/Plutone11011/PlutonBot')
    else:
        reply_markup = ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat_id, text="I'm back.", reply_markup=reply_markup)
        return ConversationHandler.END

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token='698307431:AAG9kExmheQ5hLvBieJNtsTqV9M4U_GNFv0') #updater fetches new update from telegram, passing it to the dispatcher class


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # Add conversation handler with the states NAME and OBJECTS
    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NAME : [MessageHandler(Filters.text, name)],

            OBJECTS : [MessageHandler(Filters.text, ogg)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('help',help)],

        states={
            HELP : [MessageHandler(Filters.text,helper)]
        },
        fallbacks = [CommandHandler('cancel',cancel)]
    )
    

    dp.add_handler(conv_handler1)
    dp.add_handler(conv_handler2)

    dp.add_handler(CommandHandler('print', print_stuff))

    dp.add_handler(CommandHandler('help', help))    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
