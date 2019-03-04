# -*- coding: utf-8 -*-
import os
import logging
import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import redis

# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
port = int(os.environ['PORT'])
r_server = redis.from_url(os.environ['REDIS_URL'])

#some_api_token = os.environ['SOME_API_TOKEN'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MEMBERS, RECOMMENDATIONS = range(2)


def createRedisDB():
    #creates a set of redis key-value pairs with json-like string as values, if the keys don't exist already
    r_server.msetnx({"people":'["Rolenzo","John_Smith","Endeavor","Raffaele","MaD","Alberto","Zacco","Plutone"]',
        "Rolenzo":'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Plutone":[],"Zacco":[],"Alberto":[],"John_Smith":[],"Endeavor":[]}',
        "Raffaele":'{"isBeingRecommended":false,"Rolenzo":[],"MaD":[],"Plutone":[],"Zacco":[],"Alberto":[],"John_Smith":[],"Endeavor":[]}',
        "Endeavor":'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Plutone":[],"Zacco":[],"Alberto":[],"John_Smith":[],"Rolenzo":[]}',
        "Plutone":'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Rolenzo":[],"Zacco":[],"Alberto":[],"John_Smith":[],"Endeavor":[]}',
        "MaD":'{"isBeingRecommended":false,"Raffaele":[],"Rolenzo":[],"Plutone":[],"Zacco":[],"Alberto":[],"John_Smith":[],"Endeavor":[]}',
        "Alberto":'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Plutone":[],"Zacco":[],"Rolenzo":[],"John_Smith":[],"Endeavor":[]}',
        "John_Smith":'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Plutone":[],"Zacco":[],"Rolenzo":[],"Alberto":[],"Endeavor":[]}',
        Zacco:'{"isBeingRecommended":false,"Raffaele":[],"MaD":[],"Plutone":[],"Alberto":[],"Rolenzo":[],"John_Smith":[],"Endeavor":[]}'})


#every callback must feature bot and update as positional arguments
def help(bot,update):
    update.message.reply_text('Hi, I\'m a bot. I will help you recommend stuff you like to your friends.\n' +
    'Here\'s a list of available commands\n '+
    '/add - give an advice to a friend\n'+    
    '/remove - cancel a wrong recommendation. You don\'t want them to think you have shit taste!\n'+
    '/get - visualize the recommendations your friends made for you')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def add(bot, update):
    custom_keyboard = [[InlineKeyboardButton('Rolenzo',callback_data='Rolenzo')],[InlineKeyboardButton('Raffaele',callback_data='Raffaele')],
        [InlineKeyboardButton('Zacco',callback_data='Zacco')],[InlineKeyboardButton('Endeavor',callback_data='Endeavor')],
        [InlineKeyboardButton('MaD',callback_data='MaD')],[InlineKeyboardButton('John_Smith',callback_data='John_Smith')],
        [InlineKeyboardButton('Plutone',callback_data='Plutone')],[InlineKeyboardButton('Alberto',callback_data='Alberto')],]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)    
    update.message.reply_text('Choose the person you want to advise', reply_markup=reply_markup)
    return MEMBERS

def member(bot,update):
    #search for the right person to return recommendations thanks to the callback_data of the inline keyboard buttons
    recommendations = r_server.get(update.callback_query.data)
    #parse it and return a python dictionary
    recommendations_as_dict = json.loads(recommendations)
    recommendations_as_dict["isBeingRecommended"] = True
    #need to do the inverse and re-set the redis db with the flag set
    recommendations = json.dumps(recommendations_as_dict)
    r_server.set(update.callback_query.data,recommendations)
    
    update.callback_query.message.reply_text('Type in something to suggest to the victim')
    return RECOMMENDATIONS

def fin(bot,update):
    #searches for the user who's actually being recommended in this conversation
    #then applies the recommendation
    for user in json.loads(r_server.get("users")):
        recommendations_as_dict = json.loads(r_server.get(user)) 
        if recommendations_as_dict["isBeingRecommended"]:
            recommendations_as_dict[update.message.from_user.username].append(update.message.text)
            recommendations_as_dict[isBeingRecommended] = False
            r.server.set(user,json.dumps(recommendations_as_dict))
    
    return ConversationHandler.END



def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():

    createRedisDB()
    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0",port=port, url_path=token)
    updater.bot.setWebhook("https://advisorplutone.herokuapp.com/" + token)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # need to handle keyboard response
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],

        states={
            MEMBERS : [CallbackQueryHandler(member)],
            RECOMMENDATIONS : [MessageHandler(Filters.text, fin)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(add_conv_handler)

    dp.add_handler(CommandHandler('help', help))    
    # log all errors
    dp.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
