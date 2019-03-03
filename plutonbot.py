# -*- coding: utf-8 -*-
import os
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Updater, CommandHandler


# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
port = int(os.environ['PORT'])

#some_api_token = os.environ['SOME_API_TOKEN'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MEMBERS, RECOMMENDATIONS = range(2)

custom_keyboard = [['Rolenzo','Raffaele'], ['Zacco',"Endeavor"],["Ma D.","John Smith"],["Plutone","Tutti"]]
reply_markup = ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True)

#every callback must feature bot and update as positional arguments
def help(bot,update):
    update.message.reply_text('Hi, I\'m a bot. I will help you recommend stuff you like to your friends.\n' +
    'Here\'s a list of available commands\n '+
    '/add - give an advice to a friend\n'+    
    '/remove - cancel a wrong recommendation. You don\'t want them to think you have shit taste!'+
    '/get - visualize the recommendations your friends made for you'    )

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def add(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Choose the person you want to advise", reply_markup=reply_markup)
    return MEMBERS

def member(bot,update):
    print(update.message.reply_text)
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():

    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0",port=port, url_path=token)
    updater.bot.setWebhook("https://advisorplutone.herokuapp.com/" + token)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # need to handle keyboard response
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],

        states={
            MEMBERS : [MessageHandler(Filters.text, member)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    

    dp.add_handler(CommandHandler('add',add))

    dp.add_handler(CommandHandler('help', help))    
    # log all errors
    dp.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
