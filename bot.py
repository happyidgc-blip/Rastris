import telebot
from flask import Flask, request
import os

BOT_TOKEN = "8493211054:AAGs7vffZ7ONzz43XiErMbLeONMSbqSLElU"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Hello! Bot is working!")

if __name__ == '__main__':
    bot.remove_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
