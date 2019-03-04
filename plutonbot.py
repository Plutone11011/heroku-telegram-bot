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

MEMBERS, FIN = range(2)
GET = 0

custom_keyboard = [[InlineKeyboardButton('Rolenzo',callback_data='Rolenzo')],[InlineKeyboardButton('Raffaele',callback_data='Raffaele')],
    [InlineKeyboardButton('Zacco',callback_data='Zacco')],[InlineKeyboardButton('Endeavor',callback_data='Endeavor')],
    [InlineKeyboardButton('MaD',callback_data='MaD')],[InlineKeyboardButton('John_Smith',callback_data='John_Smith')],
    [InlineKeyboardButton('Plutone',callback_data='Plutone')],[InlineKeyboardButton('Alberto',callback_data='Alberto')],
    [InlineKeyboardButton('Everyone',callback_data='Everyone')]]
reply_markup = InlineKeyboardMarkup(custom_keyboard)


def createRedisDB():
    #creates a set of redis key-value pairs with json-like string as values, if the keys don't exist already
    r_server.mset({"users":'["Rolenzo","John_Smith","Endeavor","Raffaele","MaD","Alberto","Zacco","Plutone"]',
        "Rolenzo":'{"isBeingRecommended":false, "recs":[]}',
        "Raffaele":'{"isBeingRecommended":false,"recs":[]}',
        "Endeavor":'{"isBeingRecommended":false,"recs":[]}',
        "Plutone":'{"isBeingRecommended":false,"recs":[]}',
        "MaD":'{"isBeingRecommended":false,"recs":[]}',
        "Alberto":'{"isBeingRecommended":false,"recs":[]}',
        "John_Smith":'{"isBeingRecommended":false,"recs":[]}',
        "Zacco":'{"isBeingRecommended":false,"recs":[]}'})


#every callback must feature bot and update as positional arguments
def help(bot,update):
    update.message.reply_text('Hi, I\'m a bot. I will help you recommend stuff you like to your friends.\n' +
    'Here\'s a list of available commands\n '+
    '/add - give an advice to a friend\n'+
    '/get - visualize the recommendations your friends made for you\n'+
    '/cancel - if you changed your mind and want to stop an ongoing operation')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def add(bot, update):    
    update.message.reply_text('Choose the person you want to advise', reply_markup=reply_markup)
    return MEMBERS

def member(bot,update):

    if update.callback_query.data != 'Everyone':
        #search for the right person to return recommendations thanks to the callback_data of the inline keyboard buttons
        recommendations = r_server.get(update.callback_query.data)
        #parse it and return a python dictionary
        recommendations_as_dict = json.loads(recommendations)
        recommendations_as_dict["isBeingRecommended"] = True
        #need to do the inverse and re-set the redis db with the flag set
        recommendations = json.dumps(recommendations_as_dict)
        r_server.set(update.callback_query.data,recommendations)
    else:
        for user in json.loads(r_server.get("users")):
            recommendations_as_dict = json.loads(r_server.get(user))
            recommendations_as_dict["isBeingRecommended"] = True
            recommendations = json.dumps(recommendations_as_dict)
            r_server.set(user,recommendations)
    
    update.callback_query.message.reply_text('Type in something to suggest to the victim')
    return FIN

def fin(bot,update):
    #searches for the user who's actually being recommended in this conversation
    #then applies the recommendation
    for user in json.loads(r_server.get("users")):
        recommendations_as_dict = json.loads(r_server.get(user)) 
        if recommendations_as_dict["isBeingRecommended"]:
            recommendations_as_dict["recs"].append(update.message.text + '@' + update.message.from_user.username)
            recommendations_as_dict["isBeingRecommended"] = False
            r_server.set(user,json.dumps(recommendations_as_dict))
    update.message.reply_text("If you want to keep adding recommendations type /add, or /get to view them. Type /help if you're unsure of what to do")
    return ConversationHandler.END

def get(bot, update):
    update.message.reply_text('Choose the person whose recommendations you want to see', reply_markup=reply_markup)
    return GET

def getRec(bot, update):
    out = ''
    if update.callback_query.data != 'Everyone':
        recommendations_as_dict = json.loads(r_server.get(update.callback_query.data))
        if recommendations_as_dict["recs"]:
            for rec in recommendations_as_dict["recs"]:
                r, user = rec.split("@")
                out += r + ' by ' + '<b>'+user+'</b>' + '\n'
                update.callback_query.message.reply_text(out,parse_mode='HTML')
        else:
            update.callback_query.message.reply_text("Ops, looks like there's nothing to see here")
    else:
        for user in json.loads(r_server.get("users")):
            recommendations_as_dict = json.loads(r_server.get(user))
            if recommendations_as_dict["recs"]:
                out = '<b>'+ user + '</b>' + '\n'
                for rec in recommendations_as_dict["recs"]:
                    r, recommender = rec.split("@")
                    out += r + ' by ' + '<b>'+ recommender +'</b>'+ '\n'
                    update.callback_query.message.reply_text(out,parse_mode='HTML')
                out = '' #need to empty it for other users
    update.callback_query.message.reply_text("If you want to keep viewing recommendations type /get, or /add to contribute. Type /help if you're unsure of what to do")
    return ConversationHandler.END

def cancel(bot, update):

    #in case the user has decided to cancel the adding operation between adding the person and the item
    #need to update the flag to leave the db in a consistent state
    for user in json.loads(r_server.get("users")):
        recommendations_as_dict = json.loads(r_server.get(user))
        recommendations_as_dict["isBeingRecommended"] = False
        r_server.set(user,json.dumps(recommendations_as_dict))



    update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END

def main():

    createRedisDB()
    updater = Updater(token)
    updater.start_webhook(listen="0.0.0.0",port=port, url_path=token)
    updater.bot.setWebhook("https://advisorplutone.herokuapp.com/" + token)


    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add)],

        states={
            MEMBERS : [CallbackQueryHandler(member)],
            FIN : [MessageHandler(Filters.text, fin)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    get_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('get', get)],

        states={
            GET: [CallbackQueryHandler(getRec)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(add_conv_handler)
    dp.add_handler(get_conv_handler)

    dp.add_handler(CommandHandler('help', help))    
    # log all errors
    dp.add_error_handler(error)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
