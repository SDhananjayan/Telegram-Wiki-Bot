#dependencies
from typing import Final
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

#logging/debugging
print('Starting up bot...')

#bot-specific keys/variables
TOKEN: Final = 'bot\'s token'
BOT_USERNAME: Final = 'bot\'s username'


#Commands defns
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('You need to type wiki followed by the topic you\'re looking for. For example, "wiki tamilnadu"\
 will give you the summary of the wikipedia article on tamilnadu. Note that the summary is restricted to 500 characters')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Type hello, how are you, i am fine or unary operator and have some fun')


#helper function which gets summary from wikipedia
def get_wiki_summary(topic):
    #for debugging
    print(topic)
    queryapi = "https://en.wikipedia.org/w/api.php?"
    params = {'action':'query',
            'format':'json',
            'list':'search',
            'utf8':1,
            'srsearch':topic}
    response = requests.get(queryapi,params=params)
    #debugging
    print('requests 1 done bro')
    # Check if the request was successful
    if response.status_code == 200:
        # Get the Wikipedia summary from the response
        print("successful response")
        data = response.json()
        print(data)
        try:
            if not data["query"]["search"]:
                print("wikipedia page not found")
                return "Error: Could not get Wikipedia link for " + topic
            page = data["query"]["search"][0]["title"]
        except KeyError:
            print("wikipedia page not found")
            return "Error: Could not get Wikipedia link for " + topic
        print("found wikipedia page")
        params = {'action':'query',
            'format':'json',
            'titles': page,
            'prop': 'extracts',
            'exintro':True,
            'explaintext': True}
        response = requests.get(queryapi,params=params)
        data = response.json()
        print(data)
        page = next(iter(data['query']['pages'].values()))
        summary = page['extract'][:500]#design decision to limit to 1st 500 chars, because long text not supported by telegram
        return summary
    else:
        print("link not found")
        # Return an error message
        return "Error: Could not get Wikipedia link for " + topic
   
#response handling part
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if processed[:5]=='wiki ':
        print("found wiki")
        topic: str = processed[5:]
        return get_wiki_summary(topic)
    if processed[:5]=='hello':
        return 'Hey there!'
    if 'how are you' in processed:
        return 'I\'m good! How are you?'
    if 'not fine' in processed:
        return 'Don\'t worry. Things will get better. Just be patient.'
    if 'fine' in processed:
        return 'Nice to hear'
    if 'unary operator' in processed:
        return 'vskssnr'
    return 'I don\'t understand'

#message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get basic info of the incoming message(Get to know if it is private or group chat), so that we can send responses accordingly
    message_type: str = update.message.chat.type
    text: str = update.message.text

    # Print a log for debugging
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    # React to group messages only if users mention the bot directly
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()#removing bot name from text to which we must respond
            response: str = handle_response(new_text)
        else:
            return  # We don't want the bot respond if it's not mentioned in the group
    else:
        # Reply normal if the message is in private
        response: str = handle_response(text)
    print('Bot:', response)
    await update.message.reply_text(response)


# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    # Run the bot
    app.run_polling(poll_interval=5)
