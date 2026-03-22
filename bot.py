import telebot
import json
import os
import urllib.parse
import requests
import time
from datetime import datetime
from flask import Flask, request

# ==================== CONFIG ====================
BOT_TOKEN = "8493211054:AAGs7vffZ7ONzz43XiErMbLeONMSbqSLElU"
UPI_ID = "your-upi@okhdfcbank"  # CHANGE TO YOUR UPI ID

# File paths
USERS_FILE = "users.json"
ACCOUNTS_FILE = "accounts.json"
CODES_FILE = "codes.json"
USER_STATE_FILE = "userState.json"

# Default password
DEFAULT_PASSWORD = "111777"

# Prices
PRICES = {
    'fresh': 15,
    'prepaid': 60,
    'old': 40,
    'igcc': 120
}

# Premium Emoji IDs
EMOJI = {
    "loading": "6289785914851859832",
    "money": "5429651785352501917",
    "pin": "5382164415019768638",
    "star": "5267500801240092311",
    "plane": "5298719183347932250",
    "rocket": "5201691993775818138",
    "check": "5370972705203966197",
    "crown": "5433758796289685818",
    "shopping": "5193177581888755275",
    "heart_white": "5195033767969839232",
    "fire": "5451636889717062286",
    "phone": "5370972705203966197",
    "shopping_bag": "5197288647275071607",
    "money_icon": "5289519844436234080",
    "prepaid_icon": "5370807361847970086",
    "fresh_icon": "6176957119690970952",
    "igcc_icon": "5370871923796363520",
    "balance_icon": "5197434882321567830",
    "old_icon": "5195033767969839232",
    "stock_icon": "5472026645659401564",
    "contact_icon": "5433758796289685818",
    "check_button": "6267225207560214192",
    "exit": "6267000941547885720",
    "insufficient": "6237718408574539239",
    "required": "5408889020090449272",
    "current": "5289519844436234080",
    "calendar": "5472026645659401564",
    "time": "6176701809655029409",
    "broadcast1": "6176767054503221291",
    "broadcast2": "5451636889717062286",
    "message": "6176767054503221291",
    "thanks": "6179268421981574547",
    "rainbow": "6181321291795011350"
}

# ==================== INIT ====================
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ==================== HELPER FUNCTIONS ====================
def load_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def format_emoji(emoji_id, fallback):
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

# Load data
users = load_data(USERS_FILE)
accounts = load_data(ACCOUNTS_FILE)
codes = load_data(CODES_FILE)
user_state = load_data(USER_STATE_FILE)

# Initialize accounts
for account_type in ['fresh', 'prepaid', 'old', 'igcc', 'cc']:
    if account_type not in accounts:
        accounts[account_type] = []

def register_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            'balance': 0,
            'joined': datetime.now().strftime('%d-%m-%Y')
        }
        save_data(USERS_FILE, users)
        return True
    return False

def is_admin(user_id):
    # Add your admin IDs here
    admin_ids = [7167704900]  # @ZenoRealWebs
    return user_id in admin_ids

# ==================== MENUS ====================
def show_main_menu(chat_id):
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton('ADD FUNDS'),
        KeyboardButton('BUY PREPAID')
    )
    keyboard.add(
        KeyboardButton('BUY FRESH IG'),
        KeyboardButton('BUY IGCC')
    )
    keyboard.add(
        KeyboardButton('MY BALANCE'),
        KeyboardButton('BUY OLD IG')
    )
    keyboard.add(
        KeyboardButton('STOCK'),
        KeyboardButton('CONTACT')
    )
    keyboard.add(
        KeyboardButton('BUY CC SHOP CC')
    )
    
    msg = (f"{format_emoji(EMOJI['heart_white'], '🤍')} <b>TOP QUALITY IGS BOT</b> {format_emoji(EMOJI['heart_white'], '🤍')}\n\n"
           f"{format_emoji(EMOJI['fire'], '🔥')} <b>WELCOME TO OUR BOT</b> {format_emoji(EMOJI['fire'], '‼️')}\n\n"
           f"{format_emoji(EMOJI['phone'], '☎️')} <b>ANY PROBLEM? CONTACT : @ZenoRealWebs / @HappyBhai911</b> {format_emoji(EMOJI['phone'], '☎️')}\n\n"
           f"{format_emoji(EMOJI['shopping_bag'], '🛍️')} <b>Join Gc : @WeAreSuspecious</b> {format_emoji(EMOJI['shopping_bag'], '🛍️')}\n"
           "──────────────────────\n"
           f"{format_emoji(EMOJI['loading'], '⚡')} <b>CHOOSE BUTTONS DOWN</b> {format_emoji(EMOJI['loading'], '⚡')}\n"
           "──────────────────────")
    
    bot.send_message(chat_id, msg, parse_mode='HTML', reply_markup=keyboard)

def show_quantity_options(chat_id, account_type):
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    
    price = PRICES[account_type]
    display = account_type.upper()
    if display == 'IGCC':
        display = 'IGCC'
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(f"{display} 5", f"{display} 10", f"{display} 15", f"{display} 20")
    keyboard.row('EXIT')
    
    msg = (f"{format_emoji(EMOJI['prepaid_icon'], '🛒')} <b>WANNA BUY {display} IGS?</b> {format_emoji(EMOJI['prepaid_icon'], '🛒')}\n\n"
           f"{format_emoji(EMOJI['balance_icon'], '💰')} <b>PRICE PER {display} : ₹{price}</b> {format_emoji(EMOJI['balance_icon'], '💰')}\n"
           f"{format_emoji(EMOJI['plane'], '🔢')} <b>WANT TO BUY ASAP? (Min 5)</b> {format_emoji(EMOJI['plane'], '🔢')}")
    
    bot.send_message(chat_id, msg, parse_mode='HTML', reply_markup=keyboard)

# ==================== BOT HANDLERS ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    if str(user_id) not in user_state:
        user_state[str(user_id)] = {'step': 'main', 'data': {}}
    
    show_main_menu(chat_id)

@bot.message_handler(func=lambda m: m.text == 'ADD FUNDS')
def add_funds_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    bot.send_message(chat_id, f"{format_emoji(EMOJI['loading'], '⏳')} Please wait.. Generating QR {format_emoji(EMOJI['loading'], '📷')}", parse_mode='HTML')
    
    qr_data = f"upi://pay?pa={UPI_ID}&pn=ZENO&cu=INR"
    qr_url = f"https://quickchart.io/qr?text={urllib.parse.quote(qr_data)}&size=300"
    
    msg = (f"{format_emoji(EMOJI['money'], '💰')} <b>ADD FUNDS</b> {format_emoji(EMOJI['money'], '💰')}\n\n"
           f"{format_emoji(EMOJI['pin'], '📌')} <b>UPI ID:</b> <code>{UPI_ID}</code> {format_emoji(EMOJI['pin'], '📌')}\n\n"
           f"{format_emoji(EMOJI['star'], '⭐')} <b>WANT TO ADD FUNDS</b> {format_emoji(EMOJI['star'], '⭐')}\n\n"
           f"{format_emoji(EMOJI['plane'], '🛫')} <b>SCAN QR CODE TO PAY</b> {format_emoji(EMOJI['plane'], '🛫')}\n\n"
           f"{format_emoji(EMOJI['rocket'], '🚀')} <b>AFTER PAYING CLICK ON CHECK BUTTON</b> {format_emoji(EMOJI['rocket'], '🚀')}")
    
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text='CHECK',
        url='https://t.me/ZenoRealWebs?text=i%20Want%20To%20Add%20Funds'
    ))
    
    try:
        bot.send_photo(chat_id, qr_url, caption=msg, parse_mode='HTML', reply_markup=keyboard)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

@bot.message_handler(func=lambda m: m.text in ['BUY FRESH IG', 'BUY PREPAID', 'BUY OLD IG', 'BUY IGCC'])
def buy_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    text_map = {
        'BUY FRESH IG': 'fresh',
        'BUY PREPAID': 'prepaid',
        'BUY OLD IG': 'old',
        'BUY IGCC': 'igcc'
    }
    
    account_type = text_map[message.text]
    
    if str(user_id) not in user_state:
        user_state[str(user_id)] = {}
    user_state[str(user_id)]['step'] = 'select_quantity'
    user_state[str(user_id)]['data'] = {'type': account_type}
    save_data(USER_STATE_FILE, user_state)
    
    show_quantity_options(chat_id, account_type)

@bot.message_handler(func=lambda m: m.text == 'MY BALANCE')
def balance_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    balance = users[str(user_id)]['balance']
    username = message.from_user.username or str(user_id)
    
    msg = (f"{format_emoji(EMOJI['calendar'], '✅')} <b>YOUR ACCOUNT HAS BEEN FETCHED DONE</b> {format_emoji(EMOJI['calendar'], '✅')}\n\n"
           f"{format_emoji(EMOJI['star'], '📋')} <b>YOUR ACCOUNT DETAILS</b> {format_emoji(EMOJI['star'], '📋')}\n\n"
           f"{format_emoji(EMOJI['prepaid_icon'], '😍')} <b>USER</b> - @{username} {format_emoji(EMOJI['prepaid_icon'], '😍')}\n"
           f"{format_emoji(EMOJI['loading'], '💰')} <b>CURRENT FUNDS</b> - ₹{balance} {format_emoji(EMOJI['loading'], '💰')}\n"
           f"{format_emoji(EMOJI['thanks'], '🤑')} <b>YOUR CHAT ID</b> - <code>{user_id}</code> {format_emoji(EMOJI['thanks'], '🤑')}")
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'STOCK')
def stock_handler(message):
    chat_id = message.chat.id
    
    msg = (f"{format_emoji(EMOJI['star'], '⭐')} <b>SEE ALL STOCKS</b> {format_emoji(EMOJI['star'], '⭐')}\n\n"
           f"{format_emoji(EMOJI['fresh_icon'], '✨')} <b>FRESH IG :</b> {len(accounts.get('fresh', []))} {format_emoji(EMOJI['fresh_icon'], '✨')}\n"
           f"{format_emoji(EMOJI['prepaid_icon'], '🛒')} <b>PREPAID IG :</b> {len(accounts.get('prepaid', []))} {format_emoji(EMOJI['prepaid_icon'], '🛒')}\n"
           f"{format_emoji(EMOJI['old_icon'], '📀')} <b>OLD IG :</b> {len(accounts.get('old', []))} {format_emoji(EMOJI['old_icon'], '📀')}\n"
           f"{format_emoji(EMOJI['igcc_icon'], '🔥')} <b>IGCC :</b> {len(accounts.get('igcc', []))} {format_emoji(EMOJI['igcc_icon'], '🔥')}\n"
           f"{format_emoji(EMOJI['balance_icon'], '💳')} <b>CC / CARDS :</b> {len(accounts.get('cc', []))} {format_emoji(EMOJI['balance_icon'], '💳')}")
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'CONTACT')
def contact_handler(message):
    chat_id = message.chat.id
    
    msg = (f"{format_emoji(EMOJI['crown'], '👑')} <b>OWNER : @ZenoRealWebs / @HappyBhai911</b> {format_emoji(EMOJI['crown'], '👑')}\n\n"
           f"{format_emoji(EMOJI['shopping_bag'], '🛍️')} <b>JOIN GC : @WeAreSuspecious</b> {format_emoji(EMOJI['shopping_bag'], '🛍️')}\n\n"
           f"{format_emoji(EMOJI['check'], '💬')} <b>FOR HELP, PAYMENT ISSUES</b> {format_emoji(EMOJI['check'], '💬')}\n"
           f"{format_emoji(EMOJI['calendar'], '📱')} <b>REPLY WITHIN 24 HOURS</b> {format_emoji(EMOJI['calendar'], '📱')}\n\n"
           f"{format_emoji(EMOJI['thanks'], '✨')} <b>THANKS FOR USING MY BOT !!</b> {format_emoji(EMOJI['thanks'], '✨')}")
    
    bot.send_message(chat_id, msg, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == 'BUY CC SHOP CC')
def cc_shop_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    if str(user_id) not in user_state:
        user_state[str(user_id)] = {}
    user_state[str(user_id)]['step'] = 'cc_qty'
    user_state[str(user_id)]['data'] = {}
    save_data(USER_STATE_FILE, user_state)
    
    from telebot.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('CC 1', 'CC 2', 'CC 3', 'CC 4', 'CC 5')
    keyboard.row('CC 6', 'CC 7', 'CC 8', 'CC 9', 'CC 10')
    keyboard.row('CC 11', 'CC 12', 'CC 13', 'CC 14', 'CC 15')
    keyboard.row('CC 16', 'CC 17', 'CC 18', 'CC 19', 'CC 20')
    keyboard.row('EXIT')
    
    msg = (f"{format_emoji(EMOJI['shopping_bag'], '🛍️')} <b>CC SHOP CARDS</b> {format_emoji(EMOJI['shopping_bag'], '🛍️')}\n\n"
           f"{format_emoji(EMOJI['money'], '💳')} <b>Price Per CC: ₹50</b> {format_emoji(EMOJI['money'], '💳')}\n"
           f"{format_emoji(EMOJI['plane'], '🔢')} <b>Select CC Quantity (1-20)</b> {format_emoji(EMOJI['plane'], '🔢')}")
    
    bot.send_message(chat_id, msg, parse_mode='HTML', reply_markup=keyboard)

@bot.message_handler(func=lambda m: m.text == 'EXIT')
def exit_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if str(user_id) in user_state:
        user_state[str(user_id)] = {'step': 'main', 'data': {}}
        save_data(USER_STATE_FILE, user_state)
    
    bot.send_message(chat_id, f"{format_emoji(EMOJI['exit'], '❌')} <b>PURCHASE CANCELLED</b> {format_emoji(EMOJI['exit'], '❌')}", parse_mode='HTML')
    show_main_menu(chat_id)

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/redeem'))
def redeem_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    register_user(user_id)
    
    code = message.text.replace('/redeem', '').strip().upper()
    
    if code in codes and not codes[code]['used']:
        amount = int(codes[code]['amount'])
        users[str(user_id)]['balance'] += amount
        codes[code]['used'] = True
        codes[code]['used_by'] = user_id
        codes[code]['used_on'] = datetime.now().strftime('%d-%m-%Y')
        save_data(USERS_FILE, users)
        save_data(CODES_FILE, codes)
        bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '✅')} Code Redeemed!\n{format_emoji(EMOJI['money'], '💰')} ₹{amount} added.\n\n{format_emoji(EMOJI['crown'], '👛')} New Balance: ₹{users[str(user_id)]['balance']}", parse_mode='HTML')
    else:
        bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '❌')} Invalid or used code!", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text and m.text[0] == '/' and is_admin(m.from_user.id))
def admin_commands(message):
    chat_id = message.chat.id
    text = message.text
    
    if text.startswith('/broadcast'):
        msg = text.replace('/broadcast', '').strip()
        if msg:
            broadcast_msg = (f"{format_emoji(EMOJI['broadcast1'], '📢')} <b>Announcement</b> {format_emoji(EMOJI['broadcast1'], '📢')}\n\n"
                           f"{format_emoji(EMOJI['broadcast2'], '✨')} {msg} {format_emoji(EMOJI['broadcast2'], '✨')}\n\n"
                           f"{format_emoji(EMOJI['calendar'], '📆')} Today: {datetime.now().strftime('%d/%m/%Y')} {format_emoji(EMOJI['calendar'], '📆')}\n"
                           f"{format_emoji(EMOJI['time'], '⏰')} Time: {datetime.now().strftime('%I:%M %p')} {format_emoji(EMOJI['time'], '⏰')}\n\n"
                           f"{format_emoji(EMOJI['message'], '💬')} Ye Message Sabke Liye Hai! {format_emoji(EMOJI['message'], '💬')}\n"
                           f"{format_emoji(EMOJI['thanks'], '✨')} Thanks For Using <b>QUALITY iNDO BOT</b> {format_emoji(EMOJI['thanks'], '✨')}\n\n"
                           f"{format_emoji(EMOJI['rainbow'], '🌈')} THIS MESSAGE FOR EVERYONE {format_emoji(EMOJI['rainbow'], '🌈')}")
            
            sent = 0
            failed = 0
            for uid in users:
                try:
                    bot.send_message(int(uid), broadcast_msg, parse_mode='HTML')
                    sent += 1
                except:
                    failed += 1
                time.sleep(0.05)
            
            bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '✅')} Broadcast Ho Gaya!\n{format_emoji(EMOJI['calendar'], '📨')} Sent: {sent} Users\n{format_emoji(EMOJI['check'], '❌')} Failed: {failed} Users")
        else:
            bot.send_message(chat_id, f"{format_emoji(EMOJI['insufficient'], '⚠️')} Kuch Likho Bhai: /broadcast Tera Message")

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/add') and not m.text.startswith('/add_'))
def add_balance(message):
    chat_id = message.chat.id
    parts = message.text.split()
    if len(parts) == 3:
        target = parts[1]
        amount = int(parts[2])
        if str(target) in users:
            users[str(target)]['balance'] += amount
            save_data(USERS_FILE, users)
            bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '✅')} Added ₹{amount} to {target}\n{format_emoji(EMOJI['money'], '💰')} New Balance: ₹{users[str(target)]['balance']}")
        else:
            bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '❌')} User ID not found!")

# ==================== QUANTITY HANDLER ====================
@bot.message_handler(func=lambda m: m.text and m.text[0].isalpha() and m.text[-1].isdigit())
def quantity_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    parts = text.split()
    if len(parts) == 2:
        qty = int(parts[1])
        acc_type = parts[0].upper()
        
        type_map = {'FRESH': 'fresh', 'PREPAID': 'prepaid', 'OLD': 'old', 'IGCC': 'igcc'}
        
        if acc_type in type_map and qty >= 5 and qty <= 20:
            account_type = type_map[acc_type]
            
            if str(user_id) in user_state and user_state[str(user_id)].get('step') == 'select_quantity':
                expected = user_state[str(user_id)].get('data', {}).get('type')
                
                if expected == account_type:
                    price = PRICES[account_type]
                    total = price * qty
                    
                    if users[str(user_id)]['balance'] >= total:
                        if len(accounts[account_type]) >= qty:
                            msg = ""
                            emails = []
                            
                            for i in range(qty):
                                acc = accounts[account_type].pop(0)
                                msg += f"{i+1}. {acc['user'].upper()}\n"
                                if acc['email'] not in emails:
                                    emails.append(acc['email'])
                            
                            msg += "\n"
                            for email in emails:
                                msg += f"MAIL : {email}\n"
                            msg += f"PASS : {DEFAULT_PASSWORD}\n\n"
                            msg += "CLAIM ON : @FakeMailBot"
                            
                            users[str(user_id)]['balance'] -= total
                            save_data(USERS_FILE, users)
                            save_data(ACCOUNTS_FILE, accounts)
                            
                            bot.send_message(chat_id, msg, parse_mode='HTML')
                            
                            user_state[str(user_id)] = {'step': 'main', 'data': {}}
                            save_data(USER_STATE_FILE, user_state)
                            show_main_menu(chat_id)
                        else:
                            bot.send_message(chat_id, f"{format_emoji(EMOJI['check'], '❌')} Not enough stock! Available: {len(accounts[account_type])} accounts")
                    else:
                        bot.send_message(chat_id, f"{format_emoji(EMOJI['insufficient'], '❌')} <b>Insufficient balance !!</b> {format_emoji(EMOJI['insufficient'], '❌')}\n{format_emoji(EMOJI['required'], '💰')} <b>Required</b> - ₹{total} {format_emoji(EMOJI['required'], '💰')}\n{format_emoji(EMOJI['current'], '👛')} <b>Current Balance</b> - ₹{users[str(user_id)]['balance']} {format_emoji(EMOJI['current'], '👛')}", parse_mode='HTML')
                else:
                    bot.send_message(chat_id, "❌ Invalid selection!")
            else:
                bot.send_message(chat_id, "❌ Please select a product first!")

@bot.message_handler(func=lambda m: m.text and m.text.startswith('CC'))
def cc_quantity_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    
    if text.startswith('CC '):
        qty = int(text.replace('CC ', ''))
        
        if str(user_id) in user_state and user_state[str(user_id)].get('step') == 'cc_qty':
            if 1 <= qty <= 20:
                total = 50 * qty
                
                if users[str(user_id)]['balance'] >= total:
                    if len(accounts.get('cc', [])) >= qty:
                        msg = ""
                        for i in range(qty):
                            acc = accounts['cc'].pop(0)
                            msg += f"{i+1}. {acc['user']}|{acc['email']}\n"
                        msg += f"\nThanks For Buying ❤️\n\nREGARDS - @ZenoRealWebs / @HappyBhai911"
                        
                        users[str(user_id)]['balance'] -= total
                        save_data(USERS_FILE, users)
                        save_data(ACCOUNTS_FILE, accounts)
                        
                        bot.send_message(chat_id, msg)
                    else:
                        bot.send_message(chat_id, f"❌ Not enough CC stock! Available: {len(accounts.get('cc', []))} cards")
                else:
                    bot.send_message(chat_id, f"{format_emoji(EMOJI['insufficient'], '❌')} <b>Insufficient balance !!</b> {format_emoji(EMOJI['insufficient'], '❌')}\n{format_emoji(EMOJI['required'], '💰')} <b>Required</b> - ₹{total} {format_emoji(EMOJI['required'], '💰')}\n{format_emoji(EMOJI['current'], '👛')} <b>Current Balance</b> - ₹{users[str(user_id)]['balance']} {format_emoji(EMOJI['current'], '👛')}", parse_mode='HTML')
                
                user_state[str(user_id)] = {'step': 'main', 'data': {}}
                save_data(USER_STATE_FILE, user_state)
                show_main_menu(chat_id)

# ==================== FLASK WEBHOOK ====================
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200

@app.route('/')
def index():
    return 'Bot is running!'

if __name__ == '__main__':
    bot.remove_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
