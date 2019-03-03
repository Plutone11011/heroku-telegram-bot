# -*- coding: utf-8 -*-
import os
import logging
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler


# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
port = int(os.environ['PORT'])

#some_api_token = os.environ['SOME_API_TOKEN'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MEMBERS, RECOMMENDATIONS, FINALOBJECT = range(3)


custom_keyboard = [InlineKeyboardButton('Rolenzo',callback_data='Rolenzo'),InlineKeyboardButton('Raffaele',callback_data='Raffaele'),
    InlineKeyboardButton('Zacco',callback_data='Zacco'),InlineKeyboardButton('Endeavor',callback_data='Endeavor'),
    InlineKeyboardButton('Ma D.',callback_data='Mad D.'),InlineKeyboardButton('John Smith',callback_data='John Smith'),
    InlineKeyboardButton('Plutone',callback_data='Plutone'),InlineKeyboardButton('Tutti',callback_data='Tutti'),InlineKeyboardButton('Alberto',callback_data='Alberto')]
reply_markup = InlineKeyboardMarkup(custom_keyboard)


#every callback must feature bot and update as positional arguments
def help(bot,update):
    update.message.reply_text('Hi, I\'m a bot. I will help you recommend stuff you like to your friends.\n' +
    'Here\'s a list of available commands\n '+
    '/add - give an advice to a friend\n'+    
    '/remove - cancel a wrong recommendation. You don\'t want them to think you have shit taste!'+
    '/get - visualize the recommendations your friends made for you')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def add(bot, update):
    update.message.reply_text('Choose the person you want to advise', reply_markup=reply_markup)
    return MEMBERS

def member(bot,update,user_data):
    with open('data_sources\recommendations') as infile:
        user_data = json.load(infile)
    #if the chosen user hasn't yet received any advice from the current user, then an empty list is istantiated
    if not user_data[update.callback_query.data][update.callback_query.from_user.username]:
        user_data[update.callback_query.data][update.callback_query.from_user.username] = []

    user_data[update.callback_query.data][isBeingRecommended] = True 
    with open('data_sources\recommendations', 'w') as outfile:
        json.dump(user_data, outfile)
    
    return RECOMMENDATIONS

def rec(bot,update):
    update.message.reply_text('Type in something to suggest to the victim')
    return FINALOBJECT

def fin(bot,update,user_data):
    for recommendedDude in user_data:
        if recommendedDude[isBeingRecommended]:
            recommendedDude[update.message.from_user.username].append(update.message.text)
            recommendedDude[isBeingRecommended] = False
    
    with open('data_sources\recommendations', 'w') as outfile:
        json.dump(user_data, outfile)
    
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
            MEMBERS : [CallbackQueryHandler(callback=member,pass_user_data=True)],
            RECOMMENDATIONS : [MessageHandler(filters=Filters.text, callback=rec)],
            FINALOBJECT : [MessageHandler(filters=Filters.text, callback=fin,pass_user_data=True)]
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
