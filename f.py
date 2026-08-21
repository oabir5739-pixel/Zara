# -*- coding: utf-8 -*-
import os
import sqlite3
import threading
import time
import html
from flask import Flask
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import uuid
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔑 টোকেন এবং অ্যাডমিন আইডি
TOKEN = "8950372563:AAHDH5hPsjJfQknZAUFn9v5-W7jgWE3oMqc"
ADMIN_ID = 7196917072

FORCE_SUB_CHANNEL = "@BotAllUpdateServis"

bot = telebot.TeleBot(TOKEN)
user_temp_deposit = {}
pending_deposits = {}
admin_states = {}
order_delivery_cache = {}

# ----------------- Premium Custom Emoji Config (Buttons) -----------------
PREMIUM_EMOJIS = {
    "all_services": "5406683434124859552",
    "deposit": "5264895611517300926",
    "profile": "5325971446625758812",
    "support": "5269402556924180806",
    "restart": "6084506256427456298",
    "admin_panel": "6269458311381258421",
    "search_user": "5435907392334215552",

    "bkash": "6152327402098793153",
    "nagad": "6152331409303280461",
    "rocket": "6086803441160558654",

    "money_10": "5879991085001871624",
    "money_20": "5879991085001871624",
    "money_30": "5879991085001871624",
    "money_40": "5879991085001871624",

    "package_item": "5251680306385151250",
    "telegram_premium_cat": "5789911984283586269",
    "vpn_service_cat": "5998881947328188290",
    "mail_cat": "5253742260054409879",
    "proxy_cat": "5287292843763713628",
    "mail_item": "5967280668885913944",
    "proxy_item": "4956560549287560231",
    "qty_select": "6071063305143719063",
    "back_button": "6206505206197261313",

    "channel_join": "6206505206197261313",
    "verify_tick": "6089184854497302293",

    "open_here_btn": "5368516976048104432",
    "txt_file_btn": "6109595432441090250",

    "vpn_nord": "5861679637964262698",
    "vpn_express": "5814184382071574423",
    "vpn_ipvanish": "5816505378103365924",
    "vpn_hma": "5816862049367494010",
    "vpn_xvpn": "5816759184900754744",
    "vpn_proton": "5861679637964262698",

    "analytics": "5213107179329953547",
    "member_count_file": "5314665894406805639",
    "balance_list": "5215420556089776398",
    "download_txt": "5435932616677145539",
    "recover_balance": "6084506256427456298",
    "live_broadcast": "6219940267626078011",
    "add_balance": "6219646698021463224",
    "bulk_update": "6084506256427456298",
    "remove_money": "6068810023566317366",   # 📌 নতুন রিমুভ মানি বাটন ইমোজি
    "post_edit": "5435907392334215552",
    "button_edit": "5406683434124859552",
    "edit_service": "5269402556924180806",
    "manage_stock": "5314665894406805639",
    "approve_btn": "6269285159774720688",
    "reject_btn": "6068810023566317366",
    "refresh_data": "6084506256427456298",
    "edit_pencil": "5435907392334215552",
    "delete_trash": "6068810023566317366"
}

POST_PREMIUM_EMOJIS = {
    "welcome_heart": "6292078018638651747",
    "welcome_shop": "5350699789551935589",
    "list_point": "6068777875736109056",
    "trusted_badge": "6084746478243288096",
    "fast_speed": "6088947729352890506",
    "down_arrow": "6219700471012009032",
    "warn_icon": "6068810023566317366",
    "step_tick": "6125147242731933920",
    "support_headphone": "6282996898701775483",
    "profile_user": "5325971446625758812",
    "balance_coin": "5215420556089776398",
    "diamond_badge": "6068673795793624089",
    "id_badge": "5435907392334215552",
    "deposit_money": "6219646698021463224",
    "sendmoney_shield": "5463424023734014980",
    "bkash_method": "6152327402098793153",
    "nagad_method": "6152331409303280461",
    "rocket_method": "6086803441160558654",
    "trx_input": "5814427657609153890",
    "waiting_clock": "6122681660921092237",
    "deposit_success": "6269285159774720688",
    "buy_success": "6269285159774720688",
    "box_package": "5314665894406805639",
    "money_spent": "6219646698021463224",
    "wallet_balance": "5215420556089776398",
    "copy_down": "5435932616677145539",
    "no_stock": "6068743889659892487",
    "insufficient_bal": "6071301770317927702",
    "quantity_icon": "5220149332262528784",
    "choose_select": "5854703064887332338",
    "txt_file_caption": "6109595432441090250",
    "order_pending": "5215484787325676090",
    "order_delivered": "6219954312169136748",
    "loudspeaker": "6219940267626078011",
    "admin_crown": "6188206545277291962",
    "alarm_bell": "6283048296575408684",
    "stats_chart": "5213107179329953547",
    "username_link": "5814427657609153890",
    "telegram_premium_cat": "5789911984283586269",
    "vpn_service_cat": "5998881947328188290",
    "mail_cat": "5253742260054409879",
    "proxy_cat": "5287292843763713628",
    "camera_icon": "5244699979506788336"
}

def pe(key):
    emoji_id = POST_PREMIUM_EMOJIS.get(key, "")
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">✨</tg-emoji>'
    return ""

def get_vpn_emoji_key(vpn_name):
    low = vpn_name.lower()
    if "nord" in low: return "vpn_nord"
    if "express" in low: return "vpn_express"
    if "ipvanish" in low: return "vpn_ipvanish"
    if "hma" in low: return "vpn_hma"
    if "x vpn" in low or "x-vpn" in low: return "vpn_xvpn"
    if "proton" in low: return "vpn_proton"
    return "vpn_service_cat"

OWNER_PREMIUM_SETTING = "owner_premium"

def update_owner_premium_status(user):
    if not user or user.id != ADMIN_ID: return
    premium = getattr(user, "is_premium", None)
    if premium is None: return
    try:
        conn = sqlite3.connect("shop_bot.db", timeout=30)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (OWNER_PREMIUM_SETTING, "1" if premium else "0"))
        conn.commit()
        conn.close()
    except Exception:
        pass

def owner_has_premium():
    try:
        conn = sqlite3.connect("shop_bot.db", timeout=30)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (OWNER_PREMIUM_SETTING,))
        row = cursor.fetchone()
        conn.close()
        return bool(row and row[0] == "1")
    except Exception:
        return False

def premium_keyboard_button(text, emoji_key):
    emoji_id = PREMIUM_EMOJIS.get(emoji_key)
    if owner_has_premium() and emoji_id:
        return KeyboardButton(text, icon_custom_emoji_id=emoji_id)
    return KeyboardButton(text)

# 📌 এখানে শর্ত তুলে দিয়ে সরাসরি ইনলাইন বাটনে প্রিমিয়াম ইমোজি আইডি সেট করা হয়েছে
def premium_inline_button(text, emoji_key, callback_data=None, url=None):
    kwargs = {}
    if callback_data is not None: kwargs["callback_data"] = callback_data
    if url is not None: kwargs["url"] = url
    emoji_id = PREMIUM_EMOJIS.get(emoji_key)
    if emoji_id:
        kwargs["icon_custom_emoji_id"] = emoji_id
    return InlineKeyboardButton(text, **kwargs)

USER_LOG_FILE = "auto_member_count_user.txt"

def save_user_id_to_file(user_id):
    try:
        existing_ids = set()
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
                existing_ids = {line.strip() for line in f if line.strip()}
        if str(user_id) not in existing_ids:
            with open(USER_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{user_id}\n")
    except Exception:
        pass

def check_user_subscription(user_id):
    if ADMIN_ID and user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ['member', 'administrator', 'creator']: return True
    except Exception:
        pass
    return False

def get_force_sub_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        premium_inline_button("Join Channel", "channel_join", url=f"https://t.me/BotAllUpdateServis"),
        premium_inline_button("Verify", "verify_tick", callback_data="verify_subscription")
    )
    return markup

def get_deposit_amount_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        premium_inline_button("10 টাকা", "money_10", callback_data="depamt_10"),
        premium_inline_button("20 টাকা", "money_20", callback_data="depamt_20"),
        premium_inline_button("30 টাকা", "money_30", callback_data="depamt_30"),
        premium_inline_button("40 টাকা", "money_40", callback_data="depamt_40")
    )
    return markup

def get_payment_method_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        premium_inline_button("bKash", "bkash", callback_data="paymethod_bKash"),
        premium_inline_button("Nagad", "nagad", callback_data="paymethod_Nagad"),
        premium_inline_button("Rocket", "rocket", callback_data="paymethod_Rocket")
    )
    return markup

def auto_drive_backup_loop():
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    SERVICE_ACCOUNT_FILE = 'credentials.json' 
    PARENT_FOLDER_ID = '1Fmf22X9PIWhi1qH5q1pf_4xWGeDOMH6V' 

    while True:
        time.sleep(86400) 
        try:
            if not os.path.exists('shop_bot.db'): continue
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=creds)
            query = f"name = 'shop_bot.db' and '{PARENT_FOLDER_ID}' in parents and trashed = false"
            response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = response.get('files', [])
            media = MediaFileUpload('shop_bot.db', resumable=True)
            if files:
                service.files().update(fileId=files[0]['id'], media_body=media).execute()
            else:
                service.files().create(body={'name': 'shop_bot.db', 'parents': [PARENT_FOLDER_ID]}, media_body=media, fields='id').execute()
        except Exception:
            pass

def init_db():
    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        balance REAL DEFAULT 0.0,
                        username TEXT
                    )''')
    try: cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
    except sqlite3.OperationalError: pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                        cat_id TEXT PRIMARY KEY,
                        name TEXT,
                        price REAL,
                        has_emoji INTEGER DEFAULT 1,
                        group_type TEXT DEFAULT 'mail'
                    )''')
    try: cursor.execute("ALTER TABLE categories ADD COLUMN has_emoji INTEGER DEFAULT 1")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE categories ADD COLUMN group_type TEXT DEFAULT 'mail'")
    except sqlite3.OperationalError: pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS sub_services (
                        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cat_id TEXT,
                        sub_name TEXT,
                        price REAL,
                        has_emoji INTEGER DEFAULT 1
                    )''')
    try: cursor.execute("ALTER TABLE sub_services ADD COLUMN has_emoji INTEGER DEFAULT 1")
    except sqlite3.OperationalError: pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cat_id TEXT,
                        content TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS custom_buttons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        btn_name TEXT,
                        btn_url TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )''')
    conn.commit()

    default_posts = {
        'welcome_msg': (
            f"{pe('welcome_heart')} <b>Welcome {{first_name}}!</b> {pe('welcome_shop')} আমাদের Shop এ আপনাকে স্বাগতম।\n\n"
            f"{pe('list_point')} এখানে কম মূল্যে পেয়ে যাবেন:\n\n"
            f"{pe('list_point')} Premium Proxy\n"
            f"{pe('list_point')} Premium VPN\n"
            f"{pe('list_point')} Hotmail Account (High quality)\n"
            f"{pe('list_point')} Outlook Account (High quality)\n"
            f"{pe('list_point')} Telegram Premium Buy\n\n"
            f"{pe('trusted_badge')} <b>Trusted service</b>\n"
            f"{pe('fast_speed')} <b>Auto fast service</b>\n\n"
            f"{pe('down_arrow')} নিচের মেনু বাটনগুলো ব্যবহার করুন:"
        ),
        'not_joined_msg': (
            f"{pe('warn_icon')} <b>আপনি আমাদের চ্যানেলে Join করেননি!</b>\n\n"
            f"{pe('step_tick')} বট ব্যবহার করতে প্রথমে Join Channel এ ক্লিক করে জয়েন করুন, এরপর Verify বাটনে ক্লিক করুন।"
        ),
        'support_msg': f"{pe('support_headphone')} <b>যেকোনো প্রয়োজনে আমাদের সাপোর্ট আইডিতে যোগাযোগ করুন:</b>\nhttps://t.me/FBbuysellAX",
        'deposit_info_msg': (
            f"{pe('deposit_money')} <b>আপনি কত টাকা ডিপোজিট করতে চান সংখ্যাটি লিখে পাঠান:</b>\n\n"
            f"{pe('list_point')} সর্বনিম্ন ১০ টাকা {pe('deposit_money')}\n"
            f"{pe('list_point')} সর্বোচ্চ ১০০০০ টাকা {pe('deposit_money')}"
        )
    }

    for key, val in default_posts.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))
    conn.commit()

    cursor.execute("INSERT OR REPLACE INTO categories VALUES ('hotmail', 'Hotmail Account', 0.85, 1, 'mail')")
    cursor.execute("INSERT OR REPLACE INTO categories VALUES ('outlook', 'Outlook Account', 0.85, 1, 'mail')")
    cursor.execute("INSERT OR REPLACE INTO categories VALUES ('Outlook fr', 'Outlook fr. (High quality)', 1.0, 1, 'mail')")
    cursor.execute("INSERT OR REPLACE INTO categories VALUES ('Ig Hotmail', 'Instagram Id Create Hotmail', 0.55, 1, 'mail')")
    cursor.execute("INSERT OR REPLACE INTO categories VALUES ('proxy', 'Owl Proxy (200MB)', 7.0, 1, 'proxy')")

    cursor.execute("SELECT COUNT(*) FROM sub_services WHERE cat_id = 'telegram_premium'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (3 Month)', 2010.0, 1)")
        cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (6 Month)', 2520.0, 1)")
        cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (12 Month)', 4030.0, 1)")

    cursor.execute("SELECT COUNT(*) FROM sub_services WHERE cat_id LIKE 'vpn_%'")
    if cursor.fetchone()[0] == 0:
        vpns = ["Nord VPN", "Express VPN", "IPVanish VPN", "Hma VPN", "X VPN", "Proton VPN"]
        for v in vpns:
            cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_3d', ?, 20.0, 1)", (f"{v} (3 Day)",))
            cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_7d', ?, 35.0, 1)", (f"{v} (7 Day)",))
            cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_9d', ?, 45.0, 1)", (f"{v} (9 Day)",))
            cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_1m', ?, 95.0, 1)", (f"{v} (1 Month)",))

    conn.commit()
    conn.close()

init_db()

conn = sqlite3.connect("shop_bot.db", timeout=30)
cursor = conn.cursor()
cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (OWNER_PREMIUM_SETTING, "0"))
conn.commit()
conn.close()

def get_setting_msg(key, default=""):
    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else default

def get_permanent_keyboard(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        premium_keyboard_button("All Services", "all_services"),
        premium_keyboard_button("Deposit", "deposit")
    )
    markup.row(
        premium_keyboard_button("Profile", "profile"),
        premium_keyboard_button("Support", "support")
    )
    if user_id == ADMIN_ID:
        markup.row(
            premium_keyboard_button("Admin Panel", "admin_panel"),
            premium_keyboard_button("Search User ID", "search_user")
        )
    markup.row(premium_keyboard_button("Restart Bot", "restart"))
    return markup

def main_menu_inline(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("SELECT btn_name, btn_url FROM custom_buttons")
    custom_btns = cursor.fetchall()
    conn.close()
    for b_name, b_url in custom_btns:
        markup.add(premium_inline_button(b_name, "home_button", url=b_url))
    return markup

def get_categories_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        premium_inline_button("All Mail Service", "mail_cat", callback_data="group_mail"),
        premium_inline_button("All Proxy Service", "proxy_cat", callback_data="group_proxy"),
        premium_inline_button("Telegram Premium Buy", "telegram_premium_cat", callback_data="special_cat_telegram_premium"),
        premium_inline_button("VPN Service", "vpn_service_cat", callback_data="special_cat_vpn_service")
    )
    return markup

# 📌 অ্যাডমিন প্যানেল: এখানে 'Remove Money' বাটন যুক্ত করা হলো
def get_admin_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        premium_inline_button("Bot Analytics & Users", "analytics", callback_data="admin_analytics"),
        premium_inline_button("Auto Count Member ID", "member_count_file", callback_data="admin_auto_member_count"),
        premium_inline_button("All Member Balance List", "balance_list", callback_data="admin_member_balance_list"),
        premium_inline_button("Download Balance List TXT", "download_txt", callback_data="admin_download_balance_txt"),
        premium_inline_button("Recover Balance List (.txt)", "recover_balance", callback_data="admin_recover_balance_list"),
        premium_inline_button("Live Analysis & User Broadcast Message", "live_broadcast", callback_data="admin_live_broadcast"),
        premium_inline_button("Add Member Money Back", "add_balance", callback_data="admin_add_member_balance"),
        premium_inline_button("Remove Money", "remove_money", callback_data="admin_remove_member_balance"), # 📌 নতুন রিমুভ মানি বাটন
        premium_inline_button("Update Back All Money Member", "bulk_update", callback_data="admin_bulk_money_update"),
        premium_inline_button("All Post Edit", "post_edit", callback_data="admin_all_post_edit"),
        premium_inline_button("All Button Edit", "button_edit", callback_data="admin_all_button_edit"),
        premium_inline_button("Edit Prices & Services", "edit_service", callback_data="admin_edit_services"),
        premium_inline_button("Manage Stock (Add/Remove)", "manage_stock", callback_data="admin_add_stock_menu")
    )
    return markup

@bot.message_handler(func=lambda message: message.text and "Restart Bot" in message.text)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    update_owner_premium_status(message.from_user)
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
    save_user_id_to_file(user_id)

    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    existing_user = cursor.fetchone()
    if not existing_user:
        cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, 0.0, ?)", (user_id, first_name, username))
    else:
        cursor.execute("UPDATE users SET first_name = ?, username = ? WHERE user_id = ?", (first_name, username, user_id))
    conn.commit()
    conn.close()

    if not check_user_subscription(user_id):
        not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি আমাদের চ্যানেলে Join করেননি!")
        bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
        return

    welcome_template = get_setting_msg('welcome_msg', f"স্বাগতম {{first_name}}!")
    landing_text = welcome_template.replace("{first_name}", first_name)

    bot.send_message(message.chat.id, landing_text, parse_mode="HTML", reply_markup=main_menu_inline(user_id))
    bot.send_message(message.chat.id, f"{pe('down_arrow')} আপনার সুবিধার্থে নিচের মেনু বাটনগুলো ব্যবহার করুন:", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text and any(keyword in message.text for keyword in ["All Services", "Deposit", "Profile", "Support", "Admin Panel", "Search User ID"]))
def handle_reply_buttons(message):
    update_owner_premium_status(message.from_user)
    user_id = message.from_user.id
    text = message.text
    username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
    save_user_id_to_file(user_id)

    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
    conn.commit()
    conn.close()

    if not check_user_subscription(user_id):
        not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি এখনো চ্যানেলে Join করেননি!")
        bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
        return

    if user_id in user_temp_deposit:
        del user_temp_deposit[user_id]
    
    if "All Services" in text:
        markup = get_categories_markup()
        bot.send_message(message.chat.id, f"{pe('welcome_shop')} <b>আমাদের কাছে নিচের সার্ভিসগুলো রয়েছে:</b>", parse_mode="HTML", reply_markup=markup)

    elif "Deposit" in text:
        user_temp_deposit[user_id] = {"step": "waiting_amount"}
        msg = get_setting_msg('deposit_info_msg', (
            f"{pe('deposit_money')} <b>আপনি কত টাকা ডিপোজিট করতে চান সংখ্যাটি লিখে পাঠান:</b>\n\n"
            f"{pe('list_point')} সর্বনিম্ন ১০ টাকা\n"
            f"{pe('list_point')} সর্বোচ্চ ১০০০০ টাকা"
        ))
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=get_deposit_amount_markup())

    elif "Profile" in text:
        conn = sqlite3.connect("shop_bot.db", timeout=30)
        cursor = conn.cursor()
        cursor.execute("SELECT balance, username FROM users WHERE user_id = ?", (user_id,))
        res = cursor.fetchone()
        bal = res[0] if res else 0.0
        u_name = res[1] if res and res[1] else username
        conn.close()
        
        profile_text = (
            f"{pe('profile_user')} <b>Your Account Profile</b>\n\n"
            f"{pe('id_badge')} <b>User ID:</b> <code>{user_id}</code>\n"
            f"{pe('username_link')} <b>Username:</b> <b>{u_name}</b>\n"
            f"{pe('balance_coin')} <b>Account Balance:</b> <b>৳{bal}</b> {pe('diamond_badge')}"
        )
        bot.send_message(message.chat.id, profile_text, parse_mode="HTML")

    elif "Support" in text:
        supp_msg = get_setting_msg('support_msg', f"{pe('support_headphone')} যেকোনো প্রয়োজনে আমাদের সাপোর্ট আইডিতে যোগাযোগ করুন:\nhttps://t.me/FBbuysellAX")
        bot.send_message(message.chat.id, supp_msg, parse_mode="HTML")

    elif "Search User ID" in text and user_id == ADMIN_ID:
        admin_states[user_id] = {"action": "searching_user"}
        bot.send_message(message.chat.id, f"{pe('list_point')} ইউজারের সম্পূর্ণ তথ্য ও ব্যালেন্স দেখতে তার <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML")

    elif "Admin Panel" in text and user_id == ADMIN_ID:
        bot.send_message(message.chat.id, f"{pe('admin_crown')} <b>Admin Control Panel</b>\n\nনিচের অপশনগুলো থেকে ম্যানেজ করুন:", parse_mode="HTML", reply_markup=get_admin_markup())

def process_purchase(chat_id, user_id, cat_id, qty):
    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("SELECT price, name FROM categories WHERE cat_id = ?", (cat_id,))
    cat_data = cursor.fetchone()
    if not cat_data:
        conn.close()
        bot.send_message(chat_id, f"{pe('warn_icon')} এই সার্ভিসটি বর্তমানে আর উপলব্ধ নেই।", parse_mode="HTML")
        return

    price_per_item = cat_data[0]
    cat_name = cat_data[1]
    total_cost = price_per_item * qty

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user_balance_row = cursor.fetchone()
    user_balance = user_balance_row[0] if user_balance_row else 0.0

    if user_balance < total_cost:
        conn.close()
        bot.send_message(
            chat_id, 
            f"{pe('insufficient_bal')} <b>আপনার অ্যাকাউন্টে পর্যাপ্ত ব্যালেন্স নেই!</b>\n\n"
            f"{pe('money_spent')} প্রয়োজন: ৳{total_cost}\n"
            f"{pe('wallet_balance')} আপনার আছে: ৳{user_balance}\n\n"
            f"{pe('step_tick')} আগে ডিপোজিট করুন, তারপর পণ্য কিনুন।",
            parse_mode="HTML",
            reply_markup=get_permanent_keyboard(user_id)
        )
        return

    cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
    stock_count = cursor.fetchone()[0]

    if stock_count < qty:
        conn.close()
        bot.send_message(chat_id, f"{pe('no_stock')} দুঃখিত, এই মুহূর্তে পর্যাপ্ত স্টক নেই! স্টকে আছে: <b>{stock_count} পিস</b>።", parse_mode="HTML")
        return

    cursor.execute("SELECT id, content FROM stock WHERE cat_id = ? ORDER BY id ASC LIMIT ?", (cat_id, qty))
    items = cursor.fetchall()

    new_balance = user_balance - total_cost
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

    for item_id, content in items:
        cursor.execute("DELETE FROM stock WHERE id = ?", (item_id,))
    
    conn.commit()
    conn.close()

    raw_contents = [content.strip() for item_id, content in items]
    order_key = str(uuid.uuid4())[:8]
    order_delivery_cache[order_key] = {
        "items": raw_contents,
        "cat_name": cat_name,
        "qty": qty,
        "cat_id": cat_id
    }

    delivery_markup = InlineKeyboardMarkup(row_width=2)
    delivery_markup.add(
        premium_inline_button("Open Here", "open_here_btn", callback_data=f"show_open_{order_key}"),
        premium_inline_button("TXT File", "txt_file_btn", callback_data=f"show_txt_{order_key}")
    )

    purchase_msg = (
        f"{pe('buy_success')} <b>Purchase Successful!</b>\n\n"
        f"{pe('box_package')} Item: <b>{cat_name}</b>\n"
        f"{pe('quantity_icon')} Quantity: <b>{qty} Pcs</b>\n"
        f"{pe('money_spent')} Total Cost: <b>৳{total_cost}</b>\n"
        f"{pe('wallet_balance')} Remaining Balance: <b>৳{new_balance}</b>\n\n"
        f"{pe('choose_select')} <b>আপনার ফাইলটি বট থেকে নিতে চাচ্ছেন নাকি TXT ফাইল আকারে নিতে চাচ্ছেন সিলেক্ট করুন:</b>"
    )

    bot.send_message(chat_id, purchase_msg, parse_mode="HTML", reply_markup=delivery_markup)

# ----------------- Callbacks & Handlers -----------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    update_owner_premium_status(call.from_user)
    user_id = call.from_user.id
    username = f"@{call.from_user.username}" if call.from_user.username else "N/A"
    save_user_id_to_file(user_id)

    if call.data.startswith("show_open_"):
        order_key = call.data.replace("show_open_", "")
        if order_key in order_delivery_cache:
            data = order_delivery_cache[order_key]
            items = data["items"]
            cat_name = data["cat_name"]
            formatted_items = [f"{idx}. <code>{content}</code>" for idx, content in enumerate(items, 1)]
            open_msg = f"{pe('buy_success')} <b>{cat_name} (Total: {len(items)} Pcs)</b>\n\n{pe('copy_down')} <b>ক্লিক করে কপি করুন:</b>\n\n" + "\n\n".join(formatted_items)
            bot.send_message(call.message.chat.id, open_msg, parse_mode="HTML")
            bot.answer_callback_query(call.id, "অ্যাকাউন্টগুলো নিচে ওপেন হয়েছে!")
        else:
            bot.answer_callback_query(call.id, "এই অর্ডারের সেশনটি মেয়াদোত্তীর্ণ হয়ে গেছে।", show_alert=True)
        return

    elif call.data.startswith("show_txt_"):
        order_key = call.data.replace("show_txt_", "")
        if order_key in order_delivery_cache:
            data = order_delivery_cache[order_key]
            items, cat_name, cat_id = data["items"], data["cat_name"], data["cat_id"]
            file_path = f"{cat_id}_order.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(items))
            with open(file_path, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption=f"{pe('txt_file_caption')} <b>{cat_name}</b> এর টেক্সট ফাইল নিচে দেওয়া হলো:", parse_mode="HTML")
            os.remove(file_path)
            bot.answer_callback_query(call.id, "ফাইল পাঠানো হয়েছে!")
        else:
            bot.answer_callback_query(call.id, "এই অর্ডারের সেশনটি মেয়াদোত্তীর্ণ হয়ে গেছে।", show_alert=True)
        return

    if call.data == "verify_subscription":
        if check_user_subscription(user_id):
            conn = sqlite3.connect("shop_bot.db", timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, 0.0, ?)", (user_id, call.from_user.first_name or "User", username))
            else:
                cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
            conn.commit()
            conn.close()

            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception: pass

            bot.send_message(call.message.chat.id, f"{pe('step_tick')} আপনার একাউন্ট সফলভাবে Verify হয়েছে!\nএখন আপনি বটের সকল ফিচার ও কেনাকাটা করতে পারবেন। নিচে আপনার মেনু দেওয়া হলো:", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
        else:
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} আপনি এখনো চ্যানেলে Join করেননি! আগে চ্যানেলে জয়েন করুন তারপর Verify ক্লিক করুন।", parse_mode="HTML")
        return

    if not check_user_subscription(user_id):
        bot.send_message(call.message.chat.id, f"{pe('warn_icon')} আগে আমাদের চ্যানেলে Join করুন এবং Verify করুন!", parse_mode="HTML", reply_markup=get_force_sub_markup())
        return

    if call.data.startswith("depamt_"):
        amt = float(call.data.split("_")[1])
        user_temp_deposit[user_id] = {"amount": amt, "step": "waiting_method"}
        bot.send_message(call.message.chat.id, f"{pe('sendmoney_shield')} <b>আপনি কিসের মাধ্যমে পেমেন্ট করতে চাচ্ছেন সিলেক্ট করুন:</b>", parse_mode="HTML", reply_markup=get_payment_method_markup())
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    if call.data.startswith("paymethod_"):
        method = call.data.split("_")[1]
        amt = user_temp_deposit.get(user_id, {}).get("amount", 10.0)
        user_temp_deposit[user_id] = {
            "amount": amt,
            "method": method,
            "step": "waiting_trx"
        }
        number_map = {"bKash": "+8801842145918", "Nagad": "+8801842145918", "Rocket": "+8801842145918"}
        pay_num = number_map.get(method, "+8801842145918")
        method_pe_key = "bkash_method" if method == "bKash" else ("nagad_method" if method == "Nagad" else "rocket_method")

        msg = (
            f"{pe(method_pe_key)} আপনি <b>{method}</b> সিলেক্ট করেছেন।\n\n"
            f"{pe('sendmoney_shield')} পার্সোনাল নাম্বারে টাকা সেন্ড মানি করুন:\n"
            f"{pe(method_pe_key)} {method}: <code>{pay_num}</code>\n\n"
            f"{pe('deposit_money')} <b>{int(amt) if amt.is_integer() else amt} TK Send Money</b>\n\n"
            f"{pe('trx_input')} টাকা পাঠানোর পর আপনার ট্রানজেকশন আইডি (Transaction ID) চ্যাটে লিখে পাঠান:"
        )
        bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()

    if call.data == "admin_main":
        if user_id in admin_states: del admin_states[user_id]
        conn.close()
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('admin_crown')} <b>Admin Control Panel</b>\n\nনিচের অপশনগুলো থেকে ম্যানেজ করুন:", parse_mode="HTML", reply_markup=get_admin_markup())
        return

    elif call.data == "admin_auto_member_count" and user_id == ADMIN_ID:
        cursor.execute("SELECT user_id FROM users")
        db_users = cursor.fetchall()
        conn.close()
        
        all_unique_ids = set()
        for u in db_users:
            all_unique_ids.add(str(u[0]))
            
        if os.path.exists(USER_LOG_FILE):
            with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned: all_unique_ids.add(cleaned)
                    
        with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
            for uid in sorted(all_unique_ids):
                f.write(f"{uid}\n")
                
        if all_unique_ids:
            with open(USER_LOG_FILE, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} <b>auto_member_count_user.txt</b>\nমোট মেম্বার সংখ্যা: <b>{len(all_unique_ids)} জন</b>", parse_mode="HTML")
            bot.answer_callback_query(call.id, "ফাইল পাঠানো হয়েছে!")
        else:
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এখনো কোনো মেম্বারের ইউজার আইডি সেভ হয়নি।", parse_mode="HTML")
        return

    elif call.data == "admin_live_broadcast" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "waiting_analysis_txt_for_broadcast"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('loudspeaker')} <b>Live Analysis & User Broadcast Message</b>\n\nবট এনালাইসিস বা <code>auto_member_count_user.txt</code> ফাইলটি সরাসরি এখানে ফাইল আকারে পাঠান:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data == "admin_add_member_balance" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "waiting_member_uid_for_balance"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('add_balance')} <b>Add Member Money Back</b>\n\nযে ইউজারের অ্যাকাউন্টে আগের টাকা ব্যাক দিতে চাচ্ছেন, তার সঠিক <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)
        return

    # 📌 নতুন রিমুভ মানি কলব্যাক হ্যান্ডলার
    elif call.data == "admin_remove_member_balance" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "waiting_member_uid_for_remove_money"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('remove_money')} <b>Remove Money (Balance Adjust)</b>\n\nযে ইউজারের অ্যাকাউন্ট থেকে টাকা কাট বা এডিট করতে চান, তার সঠিক <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data == "admin_bulk_money_update" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "waiting_bulk_money_data"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('bulk_update')} <b>Update Back All Money Member (Bulk Update)</b>\n\nআপনার আগের ডাউনলোড করা <code>all_member_balance_list.txt</code> ফাইলটি এখানে সরাসরি আপলোড করুন:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data == "all_services":
        conn.close()
        markup = get_categories_markup()
        bot.edit_message_text(f"{pe('welcome_shop')} <b>আমাদের কাছে নিচের সার্ভিসগুলো রয়েছে:</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "group_mail":
        cursor.execute("SELECT cat_id, name, price, has_emoji FROM categories WHERE group_type = 'mail'")
        mail_cats = cursor.fetchall()
        conn.close()

        markup = InlineKeyboardMarkup(row_width=1)
        for cat_id, name, price, has_em in mail_cats:
            sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
            sub_cur = sub_conn.cursor()
            sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
            stock_count = sub_cur.fetchone()[0]
            sub_conn.close()
            em_key = "mail_item" if has_em else None
            markup.add(premium_inline_button(f"{name} - ৳{price} (Stock: {stock_count})", em_key, callback_data=f"buy_{cat_id}"))
        markup.add(premium_inline_button("Back", "back_button", callback_data="all_services"))

        bot.edit_message_text(f"{pe('mail_cat')} <b>All Mail Services</b> {pe('mail_cat')}\n\nনিচের মেইলগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "group_proxy":
        cursor.execute("SELECT cat_id, name, price, has_emoji FROM categories WHERE group_type = 'proxy'")
        proxy_cats = cursor.fetchall()
        conn.close()

        markup = InlineKeyboardMarkup(row_width=1)
        for cat_id, name, price, has_em in proxy_cats:
            sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
            sub_cur = sub_conn.cursor()
            sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
            stock_count = sub_cur.fetchone()[0]
            sub_conn.close()
            em_key = "proxy_item" if has_em else None
            markup.add(premium_inline_button(f"{name} - ৳{price} (Stock: {stock_count})", em_key, callback_data=f"buy_{cat_id}"))
        markup.add(premium_inline_button("Back", "back_button", callback_data="all_services"))

        bot.edit_message_text(f"{pe('proxy_cat')} <b>All Proxy Services</b> {pe('proxy_cat')}\n\nনিচের প্রক্সিগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "special_cat_vpn_service":
        conn.close()
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            premium_inline_button("3 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_3d"),
            premium_inline_button("7 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_7d"),
            premium_inline_button("9 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_9d"),
            premium_inline_button("1 Month", "vpn_service_cat", callback_data="vpn_dur_vpn_1m"),
            premium_inline_button("Back", "back_button", callback_data="all_services")
        )
        bot.edit_message_text(f"{pe('vpn_service_cat')} <b>VPN Service</b> {pe('vpn_service_cat')}\n\nআপনি কতদিনের জন্য VPN নিতে চাচ্ছেন মেয়াদের ক্যাটাগরি সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("vpn_dur_"):
        dur_cat = call.data.replace("vpn_dur_", "")
        cursor.execute("SELECT sub_id, sub_name, price, has_emoji FROM sub_services WHERE cat_id = ?", (dur_cat,))
        sub_items = cursor.fetchall()
        conn.close()

        dur_text_map = {
            "vpn_3d": "৩ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_7d": "৭ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_9d": "৯ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_1m": "১ মাস মেয়াদের VPN গুলো নিচে দেওয়া হলো:"
        }
        dynamic_heading = dur_text_map.get(dur_cat, "নিচের VPN গুলো থেকে আপনার পছন্দের সার্ভিসটি সিলেক্ট করুন:")

        if not sub_items:
            bot.answer_callback_query(call.id, "এই মেয়াদের ভিপিএন বর্তমানে স্টকে নেই!", show_alert=True)
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for sub_id, sub_name, price, has_em in sub_items:
            em_key = get_vpn_emoji_key(sub_name) if has_em else None
            markup.add(premium_inline_button(f"{sub_name} - ৳{price}", em_key, callback_data=f"subbuy_{sub_id}"))
        markup.add(premium_inline_button("Back", "back_button", callback_data="special_cat_vpn_service"))

        bot.edit_message_text(f"{pe('vpn_service_cat')} <b>VPN Packages</b>\n\n{dynamic_heading}", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data == "special_cat_telegram_premium":
        cursor.execute("SELECT sub_id, sub_name, price, has_emoji FROM sub_services WHERE cat_id = 'telegram_premium'")
        sub_items = cursor.fetchall()
        conn.close()

        markup = InlineKeyboardMarkup(row_width=1)
        for sub_id, sub_name, price, has_em in sub_items:
            em_key = "telegram_premium_cat" if has_em else None
            markup.add(premium_inline_button(f"{sub_name} - ৳{price}", em_key, callback_data=f"subbuy_{sub_id}"))
        markup.add(premium_inline_button("Back", "back_button", callback_data="all_services"))

        bot.edit_message_text(f"{pe('telegram_premium_cat')} <b>Telegram Premium Buy</b> {pe('telegram_premium_cat')}\n\nনিচের প্যাকেজগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("subbuy_"):
        sub_id = call.data.split("_")[1]
        cursor.execute("SELECT cat_id, sub_name, price FROM sub_services WHERE sub_id = ?", (sub_id,))
        sub_data = cursor.fetchone()
        conn.close()

        if not sub_data:
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} দুঃখিত, এই প্যাকেজটি পাওয়া যায়নি।", parse_mode="HTML")
            return

        cat_id, sub_name, price = sub_data
        conn = sqlite3.connect("shop_bot.db", timeout=30)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        bal_res = cursor.fetchone()
        user_bal = bal_res[0] if bal_res else 0.0
        conn.close()

        if user_bal < price:
            bot.send_message(call.message.chat.id, f"{pe('insufficient_bal')} পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন ৳{price}, আপনার আছে ৳{user_bal}।", parse_mode="HTML")
            return

        user_temp_deposit[user_id] = {"step": "waiting_service_username", "cat_id": cat_id, "sub_name": sub_name, "price": price}
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass

        emoji_k = "telegram_premium_cat" if "telegram" in cat_id else get_vpn_emoji_key(sub_name)
        bot.send_message(call.message.chat.id, f"{pe(emoji_k)} আপনি সিলেক্ট করেছেন: <b>{sub_name}</b> (মূল্য: ৳{price}) {pe(emoji_k)}\n\n{pe('list_point')} এখন যে আইডিতে সার্ভিস নিতে চাচ্ছেন, সেটির সঠিক <b>Telegram Username</b> বা প্রোফাইল আইডি চ্যাটে লিখে পাঠান:", parse_mode="HTML")
        return

    elif call.data.startswith("buy_"):
        cat_id = call.data.replace("buy_", "")
        cursor.execute("SELECT name, price, group_type FROM categories WHERE cat_id = ?", (cat_id,))
        cat = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
        stock_count_res = cursor.fetchone()
        stock_count = stock_count_res[0] if stock_count_res else 0
        conn.close()

        if stock_count == 0 or not cat:
            bot.send_message(call.message.chat.id, f"{pe('no_stock')} দুঃখিত! এই মুহূর্তে এই আইটেমের স্টক শেষ।", parse_mode="HTML")
            return

        back_target = f"group_{cat[2]}" if cat[2] in ('mail', 'proxy') else "all_services"

        user_temp_deposit[user_id] = {"step": "waiting_custom_qty", "cat_id": cat_id}
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            premium_inline_button("1 Pcs", "qty_select", callback_data=f"qty_{cat_id}_1"),
            premium_inline_button("5 Pcs", "qty_select", callback_data=f"qty_{cat_id}_5"),
            premium_inline_button("10 Pcs", "qty_select", callback_data=f"qty_{cat_id}_10"),
            premium_inline_button("Back", "back_button", callback_data=back_target)
        )
        msg_text = f"{pe('box_package')} <b>{cat[0]}</b>\n{pe('money_spent')} Price: ৳{cat[1]}\nStock: {stock_count} Pcs\n\nSelect quantity:\n{pe('list_point')} অধিক নিতে চাইলে নিচে চ্যাটে কাঙ্ক্ষিত পিস সংখ্যা লিখে পাঠান।"
        try: bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        except Exception: bot.send_message(call.message.chat.id, msg_text, parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("qty_"):
        parts = call.data.split("_")
        qty_str, cat_id = parts[-1], "_".join(parts[1:-1])
        conn.close()
        if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_custom_qty":
            del user_temp_deposit[user_id]
        process_purchase(call.message.chat.id, user_id, cat_id, int(qty_str))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    elif call.data.startswith("btn_emojichoice_") and user_id == ADMIN_ID:
        choice = call.data.split("_")[2]
        has_em = 1 if choice == "yes" else 0

        if user_id in admin_states and "pending_btn_data" in admin_states[user_id]:
            pdata = admin_states[user_id]["pending_btn_data"]
            mode = pdata["mode"]

            if mode == "new_cat":
                c_name, c_price = pdata["name"], pdata["price"]
                clean_id_base = "".join([c for c in c_name.lower() if c.isalnum() or c == '_'])[:12]
                new_cat_id = f"{clean_id_base}_{str(uuid.uuid4())[:6]}"
                g_type = 'proxy' if 'proxy' in c_name.lower() else 'mail'
                cursor.execute("INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?, ?)", (new_cat_id, c_name, c_price, has_em, g_type))
                conn.commit()
                bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে নতুন বাটন যুক্ত হয়েছে!\nনাম: <code>{c_name}</code>\nমূল্য: ৳{c_price}\nগ্রুপ: {'Proxy' if g_type=='proxy' else 'Mail'}", parse_mode="HTML")

            elif mode == "edit_cat":
                c_id, c_name, c_price = pdata["cat_id"], pdata["name"], pdata["price"]
                cursor.execute("UPDATE categories SET name = ?, price = ?, has_emoji = ? WHERE cat_id = ?", (c_name, c_price, has_em, c_id))
                conn.commit()
                bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে ক্যাটাগরি আপডেট হয়েছে!\nনাম: <code>{c_name}</code>\nমূল্য: ৳{c_price}", parse_mode="HTML")

            elif mode == "new_sub":
                c_id, s_name, s_price = pdata["cat_id"], pdata["name"], pdata["price"]
                cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES (?, ?, ?, ?)", (c_id, s_name, s_price, has_em))
                conn.commit()
                bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে নতুন সাব-বাটন যুক্ত হয়েছে!\nনাম: <code>{s_name}</code>\nমূল্য: ৳{s_price}", parse_mode="HTML")

            del admin_states[user_id]
        conn.close()
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        return

    # ----------------- Stock Management (Admin Panel) -----------------
    elif call.data == "admin_add_stock_menu" and user_id == ADMIN_ID:
        if user_id in admin_states: del admin_states[user_id]
        cursor.execute("SELECT cat_id, name FROM categories")
        categories = cursor.fetchall()
        conn.close()
        markup = InlineKeyboardMarkup(row_width=1)
        for cat_id, name in categories:
            sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
            sub_cur = sub_conn.cursor()
            sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
            s_count = sub_cur.fetchone()[0]
            sub_conn.close()
            markup.add(premium_inline_button(f"{name} (Stock: {s_count} Pcs)", "manage_stock", callback_data=f"manage_stock_{cat_id}"))
        
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('box_package')} <b>Stock Management:</b>\nযে সার্ভিসের স্টক ম্যানেজ করতে চান তা সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("manage_stock_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("manage_stock_", "")
        cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
        cat_res = cursor.fetchone()
        cat_name = cat_res[0] if cat_res else cat_id

        cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
        stock_count = cursor.fetchone()[0]
        conn.close()

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            premium_inline_button("Add New Stock File (.txt)", "add_balance", callback_data=f"select_stock_{cat_id}"),
            premium_inline_button("Download Current Stock (.txt)", "download_txt", callback_data=f"download_stock_{cat_id}"),
            premium_inline_button(f"Remove All Stock ({stock_count} Pcs)", "delete_trash", callback_data=f"clear_stock_{cat_id}"),
            premium_inline_button("Back", "back_button", callback_data="admin_add_stock_menu")
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('box_package')} <b>Stock Management:</b> {cat_name}\nবর্তমান স্টক সংখ্যা: <b>{stock_count} পিস</b>", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("download_stock_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("download_stock_", "")
        cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
        cat_name = cursor.fetchone()[0]
        cursor.execute("SELECT content FROM stock WHERE cat_id = ? ORDER BY id ASC", (cat_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            bot.answer_callback_query(call.id, "এই মুহূর্তে এই ক্যাটাগরিতে কোনো স্টক নেই!", show_alert=True)
            return

        file_content = "\n".join([r[0] for r in rows])
        file_path = f"stock_{cat_id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        with open(file_path, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} <b>{cat_name}</b> এর বর্তমান সমস্ত স্টক ফাইল:", parse_mode="HTML")
        os.remove(file_path)
        return

    elif call.data.startswith("clear_stock_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("clear_stock_", "")
        cursor.execute("DELETE FROM stock WHERE cat_id = ?", (cat_id,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "স্টক সফলভাবে মুছে ফেলা হয়েছে!", show_alert=True)

        markup = InlineKeyboardMarkup(row_width=1)
        sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
        sub_cur = sub_conn.cursor()
        sub_cur.execute("SELECT cat_id, name FROM categories")
        categories = sub_cur.fetchall()
        for cid, name in categories:
            sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cid,))
            s_count = sub_cur.fetchone()[0]
            markup.add(premium_inline_button(f"{name} (Stock: {s_count} Pcs)", "manage_stock", callback_data=f"manage_stock_{cid}"))
        sub_conn.close()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))

        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('box_package')} স্টক মুছে ফেলা হয়েছে। অন্য সার্ভিস সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("select_stock_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("select_stock_", "")
        admin_states[user_id] = {"action": "waiting_stock_file", "cat_id": cat_id}
        cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
        cat_name = cursor.fetchone()[0]
        conn.close()
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data=f"manage_stock_{cat_id}"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('box_package')} আপনি সিলেক্ট করেছেন: <b>{cat_name}</b>\n\nএখন নতুন স্টক ফাইল (.txt) সরাসরি এই চ্যাটে ফাইল হিসেবে আপলোড করে পাঠান:", parse_mode="HTML", reply_markup=markup)
        return

    # ----------------- Other Admin Panel Callbacks -----------------
    elif call.data == "admin_analytics" and user_id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(balance) FROM users")
        res_sum = cursor.fetchone()
        total_user_balance = res_sum[0] if res_sum and res_sum[0] is not None else 0.0
        cursor.execute("SELECT user_id, first_name, balance FROM users ORDER BY user_id DESC")
        all_registered = cursor.fetchall()
        conn.close()

        analytics_text = (
            f"{pe('stats_chart')} <b>Live Bot Analytics & Statistics</b>\n\n"
            f"{pe('profile_user')} মোট জয়েনকৃত ইউজার: <b>{total_users} জন</b>\n"
            f"{pe('balance_coin')} ইউজারদের মোট একাউন্ট ব্যালেন্স: <b>৳{total_user_balance}</b>\n\n"
            f"{pe('list_point')} <b>সাম্প্রতিক ইউজার তালিকা:</b>\n"
        )
        for u_id, u_name, u_bal in all_registered[:15]:
            safe_name = u_name or "User"
            analytics_text += f"• {safe_name} (<code>{u_id}</code>) - ৳{u_bal}\n"

        markup = InlineKeyboardMarkup()
        markup.add(
            premium_inline_button("Download Bot Analysis TXT File", "download_txt", callback_data="admin_download_analytics_txt"),
            premium_inline_button("Refresh Live Data", "refresh_data", callback_data="admin_analytics"),
            premium_inline_button("Back", "back_button", callback_data="admin_main")
        )
        try: bot.edit_message_text(analytics_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        except Exception: pass

    elif call.data == "admin_download_analytics_txt" and user_id == ADMIN_ID:
        cursor.execute("SELECT user_id, first_name FROM users ORDER BY user_id DESC")
        all_users = cursor.fetchall()
        conn.close()

        if not all_users:
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} বোর্ডে কোনো ইউজারের ডাটা পাওয়া যায়নি!", parse_mode="HTML")
            return

        file_content = ""
        for u_id, u_name in all_users:
            safe_name = u_name or "User"
            file_content += f"{u_id} | {safe_name}\n"

        file_path = "bot_analytics_users.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        with open(file_path, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} Bot Analytics & User List (.txt)\nসকল ইউজারের আইডি দিয়ে তৈরি করা ফাইল:")
        os.remove(file_path)

    elif call.data == "admin_member_balance_list" and user_id == ADMIN_ID:
        cursor.execute("SELECT user_id, first_name, balance FROM users WHERE balance > 0 ORDER BY balance DESC")
        users_with_money = cursor.fetchall()
        conn.close()

        list_text = f"{pe('balance_coin')} <b>যেসব মেম্বারদের অ্যাকাউন্টে টাকা আছে তাদের তালিকা:</b>\n\n"
        if not users_with_money:
            list_text += f"{pe('warn_icon')} এই মুহূর্তে কারও অ্যাকাউন্টে ব্যালেন্স নেই।"
        else:
            for idx, (u_id, u_name, u_bal) in enumerate(users_with_money[:20], 1):
                safe_name = u_name or "User"
                list_text += f"{idx}. {safe_name} | ID: <code>{u_id}</code> | ব্যালেন্স: <b>৳{u_bal}</b>\n"

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            premium_inline_button("Download Balance List TXT", "download_txt", callback_data="admin_download_balance_txt"),
            premium_inline_button("Recover Balance List (.txt)", "recover_balance", callback_data="admin_recover_balance_list"),
            premium_inline_button("Back", "back_button", callback_data="admin_main")
        )
        try: bot.edit_message_text(list_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
        except Exception: pass

    elif call.data == "admin_download_balance_txt" and user_id == ADMIN_ID:
        cursor.execute("SELECT user_id, balance, first_name FROM users WHERE balance > 0 ORDER BY balance DESC")
        users_with_money = cursor.fetchall()
        conn.close()

        if not users_with_money:
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই মুহূর্তে কারও অ্যাকাউন্টে ব্যালেন্স নেই!", parse_mode="HTML")
            return

        file_content = ""
        for u_id, u_bal, u_name in users_with_money:
            file_content += f"{u_id} | {u_bal}\n"

        file_path = "all_member_balance_list.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        with open(file_path, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} All Member Balance List (.txt)\nব্যালেন্সধারী মেম্বারদের তালিকা ডাউনলোড হয়েছে:")
        os.remove(file_path)

    elif call.data == "admin_recover_balance_list" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "waiting_recover_balance_txt"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('recover_balance')} <b>Recover Balance List (.txt)</b>\n\nপূর্বে ডাউনলোড করা <code>all_member_balance_list.txt</code> ফাইলটি এখানে আপলোড করুন।", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data == "admin_all_post_edit" and user_id == ADMIN_ID:
        conn.close()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            premium_inline_button("1. Edit Welcome Post", "post_edit", callback_data="edit_post_welcome_msg"),
            premium_inline_button("2. Edit Channel Not Joined Warning", "post_edit", callback_data="edit_post_not_joined_msg"),
            premium_inline_button("3. Edit Support Text", "post_edit", callback_data="edit_post_support_msg"),
            premium_inline_button("4. Edit Deposit Information Text", "post_edit", callback_data="edit_post_deposit_info_msg"),
            premium_inline_button("Back to Admin", "back_button", callback_data="admin_main")
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('post_edit')} <b>All Post Edit</b>\n\nযেই পোস্টটি এডিট করতে চান সেটির ওপর ক্লিক করুন:", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("edit_post_") and user_id == ADMIN_ID:
        post_key = call.data.replace("edit_post_", "")
        conn.close()
        admin_states[user_id] = {"action": "waiting_generic_post_update", "post_key": post_key}
        current_text = get_setting_msg(post_key, "খালি")
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_all_post_edit"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('post_edit')} <b>Editing Post:</b> <code>{post_key}</code>\n\n<b>বর্তমান লেখা:</b>\n------------------\n{current_text}\n------------------\n\nনতুন লেখাটি পাঠান:", parse_mode="HTML", reply_markup=markup)

    elif call.data == "admin_all_button_edit" and user_id == ADMIN_ID:
        cursor.execute("SELECT cat_id, name FROM categories")
        categories = cursor.fetchall()
        cursor.execute("SELECT sub_id, sub_name FROM sub_services")
        sub_services = cursor.fetchall()
        conn.close()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton("--- Main Categories ---", callback_data="ignore"))
        for cid, name in categories:
            markup.add(premium_inline_button(name, "edit_pencil", callback_data=f"editbtn_cat_{cid}"))
        if sub_services:
            markup.add(InlineKeyboardButton("--- Sub Packages / VPNs ---", callback_data="ignore"))
            for sid, sname in sub_services:
                markup.add(premium_inline_button(sname, "edit_pencil", callback_data=f"editbtn_sub_{sid}"))
        markup.add(premium_inline_button("Back to Admin", "back_button", callback_data="admin_main"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('button_edit')} <b>All Button Edit</b>\n\nযেই বাটনটি এডিট করতে চান সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("editbtn_") and user_id == ADMIN_ID:
        parts = call.data.split("_")
        btn_type, btn_id = parts[1], "_".join(parts[2:])
        conn.close()
        admin_states[user_id] = {"action": "waiting_generic_btn_update", "btn_type": btn_type, "btn_id": btn_id}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_all_button_edit"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('edit_pencil')} এই বাটনটির জন্য নতুন <b>নাম (Text)</b> লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)

    elif call.data == "admin_edit_services" and user_id == ADMIN_ID:
        if user_id in admin_states: del admin_states[user_id]
        cursor.execute("SELECT cat_id, name, price FROM categories")
        categories = cursor.fetchall()
        conn.close()
        markup = InlineKeyboardMarkup(row_width=1)
        
        markup.add(
            premium_inline_button("Manage Sub-Buttons: All Mail Service", "edit_service", callback_data="editsubs_group_mail"),
            premium_inline_button("Manage Sub-Buttons: All Proxy Service", "edit_service", callback_data="editsubs_group_proxy")
        )
        
        special_ids = ["telegram_premium", "vpn_service"]
        regular_cats = [c for c in categories if c[0] not in special_ids and c[0] not in ['hotmail', 'outlook', 'Outlook fr', 'Ig Hotmail', 'proxy']]
        special_cats = [c for c in categories if c[0] in special_ids]
        
        for cat_id, name, price in regular_cats:
            sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
            sub_cursor = sub_conn.cursor()
            sub_cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
            stock_count = sub_cursor.fetchone()[0]
            sub_conn.close()
            markup.add(
                premium_inline_button(f"{name} | ৳{price} | Stock: {stock_count}", "edit_service", callback_data=f"editcat_{cat_id}"),
                premium_inline_button(f"Delete {name}", "delete_trash", callback_data=f"confirm_del_{cat_id}")
            )
            
        for cat_id, name, price in special_cats:
            markup.add(
                premium_inline_button(f"Manage Sub-Buttons: {name}", "edit_service", callback_data=f"editsubs_{cat_id}"),
                premium_inline_button(f"Delete {name}", "delete_trash", callback_data=f"confirm_del_{cat_id}")
            )
        
        markup.add(
            premium_inline_button("Add New Button / Service", "add_balance", callback_data="admin_add_new_btn"),
            premium_inline_button("Back", "back_button", callback_data="admin_main")
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('edit_service')} সার্ভিস এডিট বা ডিলিট করতে নিচের বাটনগুলোতে ক্লিক করুন:", parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("confirm_del_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("confirm_del_", "")
        cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
        cat_res = cursor.fetchone()
        cat_name = cat_res[0] if cat_res else "এই সার্ভিসটি"
        conn.close()

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            premium_inline_button("Yes (Delete)", "approve_btn", callback_data=f"delcat_{cat_id}"),
            premium_inline_button("No (Cancel)", "reject_btn", callback_data="admin_edit_services")
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('warn_icon')} <b>সতর্কবার্তা!</b>\n\nআপনি কি সত্যি <b>{cat_name}</b> বাটনটি ডিলিট করতে চাচ্ছেন?", parse_mode="HTML", reply_markup=markup)
        return

    elif call.data.startswith("editsubs_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("editsubs_", "")
        if cat_id == "vpn_service":
            conn.close()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                premium_inline_button("Manage 3 Day", "edit_service", callback_data="editsubs_vpn_3d"),
                premium_inline_button("Manage 7 Day", "edit_service", callback_data="editsubs_vpn_7d"),
                premium_inline_button("Manage 9 Day", "edit_service", callback_data="editsubs_vpn_9d"),
                premium_inline_button("Manage 1 Month", "edit_service", callback_data="editsubs_vpn_1m"),
                premium_inline_button("Back", "back_button", callback_data="admin_edit_services")
            )
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception: pass
            bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>VPN Service Sub-Packages Manage:</b>\nমেয়াদ অনুযায়ী প্যাকেজ ম্যানেজ করুন:", parse_mode="HTML", reply_markup=markup)
            return

        if cat_id in ("group_mail", "group_proxy"):
            g_type = 'mail' if cat_id == "group_mail" else 'proxy'
            cursor.execute("SELECT cat_id, name, price FROM categories WHERE group_type = ?", (g_type,))
            items = cursor.fetchall()
            conn.close()

            markup = InlineKeyboardMarkup(row_width=1)
            for c_id, c_name, c_price in items:
                markup.add(
                    premium_inline_button(f"Edit: {c_name} (৳{c_price})", "edit_service", callback_data=f"editcat_{c_id}"),
                    premium_inline_button(f"Delete: {c_name}", "delete_trash", callback_data=f"confirm_del_{c_id}")
                )
            
            markup.add(
                premium_inline_button("Add New Service / Button", "add_balance", callback_data="admin_add_new_btn"),
                premium_inline_button("Back", "back_button", callback_data="admin_edit_services")
            )
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception: pass
            bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>Manage {('Mail Services' if g_type=='mail' else 'Proxy Services')}:</b>", parse_mode="HTML", reply_markup=markup)
            return

        cursor.execute("SELECT sub_id, sub_name, price FROM sub_services WHERE cat_id = ?", (cat_id,))
        subs = cursor.fetchall()
        conn.close()

        markup = InlineKeyboardMarkup(row_width=1)
        for sub_id, sub_name, price in subs:
            markup.add(premium_inline_button(f"Delete: {sub_name} (৳{price})", "delete_trash", callback_data=f"delsub_{sub_id}_{cat_id}"))
        
        markup.add(
            premium_inline_button("Add New Package", "add_balance", callback_data=f"addsub_{cat_id}"),
            premium_inline_button("Back", "back_button", callback_data="admin_edit_services")
        )
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>Manage Sub-Buttons:</b>", parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("delsub_") and user_id == ADMIN_ID:
        parts = call.data.split("_")
        sub_id, cat_id = parts[1], parts[2]
        cursor.execute("DELETE FROM sub_services WHERE sub_id = ?", (sub_id,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "প্যাকেজ ডিলিট হয়েছে!")
        return

    elif call.data.startswith("addsub_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("addsub_", "")
        conn.close()
        admin_states[user_id] = {"action": "adding_sub_item", "cat_id": cat_id}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data=f"editsubs_{cat_id}"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('add_balance')} নতুন প্যাকেজের নাম এবং দাম লিখে পাঠান:\n<code>[Package Name] [Price]</code>", parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("editcat_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("editcat_", "")
        cursor.execute("SELECT name, price FROM categories WHERE cat_id = ?", (cat_id,))
        cat = cursor.fetchone()
        conn.close()
        admin_states[user_id] = {"action": "editing_cat", "cat_id": cat_id}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_edit_services"))
        edit_prompt = f"{pe('edit_pencil')} এডিট করছেন: <b>{cat[0]}</b> (বর্তমান মূল্য: ৳{cat[1]})\n\nনতুন নাম এবং রেট লিখে পাঠান।\n<b>ফরম্যাট:</b> <code>[নতুন নাম] [রেট]</code>"
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, edit_prompt, parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("delcat_") and user_id == ADMIN_ID:
        cat_id = call.data.replace("delcat_", "")
        cursor.execute("DELETE FROM categories WHERE cat_id = ?", (cat_id,))
        cursor.execute("DELETE FROM stock WHERE cat_id = ?", (cat_id,))
        cursor.execute("DELETE FROM sub_services WHERE cat_id = ?", (cat_id,))
        conn.commit()
        conn.close()
        bot.send_message(call.message.chat.id, f"{pe('step_tick')} সার্ভিসটি সফলভাবে ডিলিট করা হয়েছে!", parse_mode="HTML")

    elif call.data == "admin_add_new_btn" and user_id == ADMIN_ID:
        conn.close()
        admin_states[user_id] = {"action": "adding_new_cat"}
        markup = InlineKeyboardMarkup()
        markup.add(premium_inline_button("Back", "back_button", callback_data="admin_edit_services"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception: pass
        bot.send_message(call.message.chat.id, f"{pe('add_balance')} নতুন বাটন যোগ করতে ফরম্যাটে নাম এবং দাম লিখে পাঠান:\n<code>[Button Name] [Price]</code>", parse_mode="HTML", reply_markup=markup)

    elif call.data.startswith("app_") and user_id == ADMIN_ID:
        req_id = call.data.split("_")[1]
        if req_id in pending_deposits:
            data = pending_deposits[req_id]
            target_user, amount, method = data["user_id"], data["amount"], data.get("method", "Payment")
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_user,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_user, "User", amount))
            else:
                cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
            conn.commit()
            conn.close()
            bot.send_message(target_user, f"{pe('deposit_success')} <b>আপনার ডিপোজিট সফল হয়েছে!</b>\nআপনার একাউন্টে <b>৳{amount}</b> যোগ করা হয়েছে। এখন আপনি কেনাকাটা করতে পারেন।", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
            try:
                bot.edit_message_caption(f"Approved Successfully (User ID: {target_user}, Amount: ৳{amount}, Method: {method})", call.message.chat.id, call.message.message_id)
            except Exception:
                bot.send_message(call.message.chat.id, f"✅ Approved Successfully (User ID: {target_user}, Amount: ৳{amount})")
            del pending_deposits[req_id]
        else:
            conn.close()
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে!", parse_mode="HTML")

    elif call.data.startswith("rej_") and user_id == ADMIN_ID:
        req_id = call.data.split("_")[1]
        if req_id in pending_deposits:
            data = pending_deposits[req_id]
            target_user = data["user_id"]
            conn.close()
            bot.send_message(target_user, f"{pe('warn_icon')} আপনি ভুল তথ্য বা স্ক্রিনশট দিয়েছেন, তাই আপনার অর্ডারটি রিজেক্ট করা হলো। সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন।", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
            try:
                bot.edit_message_caption(f"Rejected (User ID: {target_user})", call.message.chat.id, call.message.message_id)
            except Exception:
                bot.send_message(call.message.chat.id, f"❌ Rejected (User ID: {target_user})")
            del pending_deposits[req_id]
        else:
            conn.close()
            bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে!", parse_mode="HTML")

    elif call.data.startswith("complete_order_") and user_id == ADMIN_ID:
        target_user = int(call.data.split("_")[2])
        conn.close()
        admin_states[user_id] = {"action": "waiting_delivery_content", "target_user": target_user}
        bot.send_message(call.message.chat.id, f"{pe('list_point')} ইউজার ID: <code>{target_user}</code> এর অর্ডারের জন্য মেসেজ বা ডাটা লিখে পাঠান:", parse_mode="HTML")

    else:
        conn.close()

# ----------------- Document/File Handler -----------------
@bot.message_handler(content_types=['document'])
def handle_stock_file(message):
    update_owner_premium_status(message.from_user)
    user_id = message.from_user.id
    save_user_id_to_file(user_id)
    
    if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
        file_id = message.document.file_id
        process_deposit_submission(message, file_id, is_document=True)
        return

    if user_id == ADMIN_ID and user_id in admin_states:
        action = admin_states[user_id].get("action")
        
        if action == "waiting_stock_file":
            cat_id = admin_states[user_id]["cat_id"]
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_content = downloaded_file.decode('utf-8', errors='ignore')
                lines = [line.strip() for line in file_content.splitlines() if line.strip()]
                
                if not lines:
                    bot.reply_to(message, f"{pe('warn_icon')} ফাইলটি খালি রয়েছে।", parse_mode="HTML")
                    return
                
                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                added_count = 0
                for line in lines:
                    cursor.execute("INSERT INTO stock (cat_id, content) VALUES (?, ?)", (cat_id, line))
                    added_count += 1
                conn.commit()
                
                cursor.execute("SELECT user_id FROM users")
                all_users = cursor.fetchall()
                cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
                cat_name = cursor.fetchone()[0]
                conn.close()
                
                broadcast_text = (
                    f"{pe('alarm_bell')} <b>নতুন স্টক আপডেট!</b>\n\n"
                    f"আমাদের বটে নতুন স্টক যুক্ত হয়েছে: <b>{cat_name}</b>\n"
                    f"এখনই আপনার অ্যাকাউন্ট থেকে পর্যাপ্ত ব্যালেন্স দিয়ে খুব সহজে কিনে নিন। স্টক সীমিত!"
                )
                for u in all_users:
                    try: bot.send_message(u[0], broadcast_text, parse_mode="HTML", reply_markup=get_permanent_keyboard(u[0]))
                    except Exception: pass

                del admin_states[user_id]
                bot.reply_to(message, f"{pe('step_tick')} সফলভাবে মোট <b>{added_count}টি</b> স্টক যোগ করা হয়েছে এবং মেম্বারদের নোটিফিকেশন পাঠানো হয়েছে!", parse_mode="HTML")
            except Exception as e:
                bot.reply_to(message, f"ফাইল প্রসেস করতে সমস্যা হয়েছে: {e}")
            return

        elif action == "waiting_recover_balance_txt":
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_content = downloaded_file.decode('utf-8', errors='ignore')
                lines = [line.strip() for line in file_content.splitlines() if line.strip()]
                
                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                recovered_count = 0
                for line in lines:
                    numbers = re.findall(r'\d+(?:\.\d+)?', line)
                    if len(numbers) >= 2:
                        try:
                            target_uid, balance_amount = int(numbers[0]), float(numbers[1])
                            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_uid,))
                            if not cursor.fetchone():
                                cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_uid, "User", balance_amount))
                            else:
                                cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (balance_amount, target_uid))
                            conn.commit()
                            recovered_count += 1
                            try:
                                bot.send_message(target_uid, f"{pe('deposit_success')} <b>ব্যালেন্স রিকভারি আপডেট!</b>\n\nআপনার একাউন্টে পূর্বের <b>৳{balance_amount}</b> জমা দেওয়া হয়েছে!", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                            except Exception: pass
                        except ValueError: pass
                
                conn.close()
                del admin_states[user_id]
                bot.reply_to(message, f"{pe('step_tick')} রিকভারি সম্পূর্ণ হয়েছে! মোট <b>{recovered_count} জন</b> ইউজারের ব্যালেন্স সফলভাবে ব্যাক করা হয়েছে।", parse_mode="HTML")
            except Exception as e:
                bot.reply_to(message, f"ফাইল প্রসেস করতে ত্রুটি ঘটেছে: {e}")
            return

        elif action == "waiting_analysis_txt_for_broadcast":
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_content = downloaded_file.decode('utf-8', errors='ignore')
                
                found_ids = re.findall(r'\b\d{6,12}\b', file_content)
                target_user_ids = list(set([int(uid) for uid in found_ids]))

                if not target_user_ids:
                    bot.reply_to(message, f"{pe('warn_icon')} ফাইল থেকে কোনো ইউজারের সঠিক আইডি খুঁজে পাওয়া যায়নি।", parse_mode="HTML")
                    return

                admin_states[user_id] = {
                    "action": "waiting_live_broadcast_message",
                    "target_uids": target_user_ids
                }

                bot.reply_to(
                    message,
                    f"{pe('step_tick')} ফাইল ডিটেকশন সফল হয়েছে! মোট <b>{len(target_user_ids)} জন</b> ইউজার পাওয়া গেছে।\n\n"
                    f"{pe('list_point')} <b>আপনি সবার উদ্দেশ্যে কি পাঠাতে চান?</b>\n"
                    f"(টেক্সট, ছবি, ভয়েস মেসেজ, ভিডিও বা ফাইল সরাসরি পাঠিয়ে দিন):",
                    parse_mode="HTML"
                )
            except Exception as e:
                bot.reply_to(message, f"ফাইল পড়তে সমস্যা হয়েছে: {e}")
            return

# ----------------- সমস্ত মেসেজ ও ডিপোজিট ফ্লো হ্যান্ডলার -----------------
def process_deposit_submission(message, file_id, is_document=False):
    update_owner_premium_status(message.from_user)
    user_id = message.from_user.id
    raw_first_name = message.from_user.first_name or "N/A"
    raw_username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
    first_name = html.escape(raw_first_name)
    username = html.escape(raw_username)
    
    save_user_id_to_file(user_id)

    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (raw_username, user_id))
    conn.commit()
    conn.close()

    if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
        data = user_temp_deposit[user_id]
        amount = data.get("amount", 0.0)
        raw_trx = str(data.get("trx_id", "N/A"))
        trx_id = html.escape(raw_trx)
        method = html.escape(str(data.get("method", "Payment")))

        bot.reply_to(
            message,
            f"{pe('waiting_clock')} <b>প্রিয় কাস্টমার দয়া করে ২ - ৩ মিনিট অপেক্ষা করুন, অ্যাকাউন্টে টাকা যোগ হচ্ছে...</b>",
            parse_mode="HTML",
            reply_markup=get_permanent_keyboard(user_id)
        )

        req_id = str(uuid.uuid4())[:8]
        pending_deposits[req_id] = {
            "user_id": user_id,
            "amount": amount,
            "trx_id": raw_trx,
            "method": method
        }
        del user_temp_deposit[user_id]

        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(
            premium_inline_button("Approve", "approve_btn", callback_data=f"app_{req_id}"),
            premium_inline_button("Reject", "reject_btn", callback_data=f"rej_{req_id}")
        )

        caption_text = (
            f"{pe('alarm_bell')} <b>New Payment Request Received!</b>\n\n"
            f"{pe('profile_user')} <b>Name:</b> <b>{first_name}</b>\n"
            f"{pe('username_link')} <b>Username:</b> <b>{username}</b>\n"
            f"{pe('id_badge')} <b>User ID:</b> <code>{user_id}</code>\n"
            f"{pe('deposit_money')} <b>Amount:</b> <b>৳{amount}</b>\n"
            f"{pe('sendmoney_shield')} <b>Payment Method:</b> <b>{method}</b>\n"
            f"{pe('trx_input')} <b>TrxID:</b> <code>{trx_id}</code>\n\n"
            f"Please verify payment and take action below:"
        )

        for i in range(3):
            try:
                bot.send_message(
                    ADMIN_ID, 
                    f"{pe('alarm_bell')} <b>[ALARM {i+1}/3] নতুন ডিপোজিট ও পেমেন্ট এসেছে! দ্রুত এপ্রুভ করুন। টং টং! 🛎️🔔</b>", 
                    parse_mode="HTML"
                )
                time.sleep(0.3)
            except Exception:
                pass

        sent_successfully = False
        try:
            if not is_document:
                bot.send_photo(ADMIN_ID, file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
            else:
                bot.send_document(ADMIN_ID, file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
            sent_successfully = True
        except Exception as e:
            print(f"Error sending photo to admin: {e}")

        if not sent_successfully:
            try:
                bot.send_message(ADMIN_ID, caption_text, parse_mode="HTML", reply_markup=admin_markup)
            except Exception:
                plain_text = f"New Deposit Received!\nUser ID: {user_id}\nAmount: {amount}\nTrxID: {raw_trx}\nMethod: {method}"
                bot.send_message(ADMIN_ID, plain_text, reply_markup=admin_markup)

@bot.message_handler(content_types=['text', 'photo', 'voice', 'audio', 'video', 'document'])
def handle_all_messages_and_broadcast(message):
    update_owner_premium_status(message.from_user)
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    save_user_id_to_file(user_id)

    conn = sqlite3.connect("shop_bot.db", timeout=30)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
    conn.commit()
    conn.close()

    if user_id == ADMIN_ID and user_id in admin_states:
        state_data = admin_states[user_id]
        action = state_data.get("action")

        if action == "waiting_live_broadcast_message":
            target_uids = state_data["target_uids"]
            del admin_states[user_id]

            bot.reply_to(message, f"{pe('waiting_clock')} <b>মেম্বারদের কাছে বার্তা পাঠানো শুরু হচ্ছে... দয়া করে কিছুক্ষণ অপেক্ষা করুন।</b>", parse_mode="HTML")

            success_count = 0
            for target_uid in target_uids:
                try:
                    if message.content_type == 'text':
                        bot.send_message(target_uid, f"{pe('loudspeaker')} <b>বিশেষ বার্তা:</b>\n\n{message.text}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    elif message.content_type == 'photo':
                        cap = message.caption or ""
                        bot.send_photo(target_uid, message.photo[-1].file_id, caption=f"{pe('loudspeaker')} <b>বিশেষ বার্তা:</b>\n\n{cap}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    elif message.content_type == 'voice':
                        bot.send_voice(target_uid, message.voice.file_id, caption=f"{pe('loudspeaker')} <b>অফিসিয়াল ভয়েস বার্তা</b>", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    elif message.content_type == 'video':
                        cap = message.caption or ""
                        bot.send_video(target_uid, message.video.file_id, caption=f"{pe('loudspeaker')} <b>বিশেষ ভিডিও:</b>\n\n{cap}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    elif message.content_type == 'document':
                        bot.send_document(target_uid, message.document.file_id, caption=f"{pe('loudspeaker')} <b>অফিসিয়াল ফাইল</b>", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    success_count += 1
                except Exception:
                    pass

            bot.send_message(
                ADMIN_ID,
                f"{pe('step_tick')} <b>ব্রডকাস্ট সম্পূর্ণ সফল হয়েছে!</b>\n"
                f"মোট পাঠানো হয়েছে: <b>{success_count} জন</b> মেম্বারের ইনবক্সে।",
                parse_mode="HTML"
            )
            return

    if message.content_type == 'photo':
        if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
            photo_id = message.photo[-1].file_id
            process_deposit_submission(message, photo_id, is_document=False)
            return

    if message.content_type != 'text':
        return

    text = message.text

    if not check_user_subscription(user_id):
        not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি এখনো আমাদের চ্যানেলে জয়েন করেননি!")
        bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
        return

    if user_id in user_temp_deposit:
        state = user_temp_deposit[user_id].get("step")

        if state == "waiting_amount":
            try:
                amount = float(text)
                if amount < 10 or amount > 10000:
                    bot.send_message(user_id, f"{pe('warn_icon')} সর্বনিম্ন ১০ টাকা এবং সর্বোচ্চ ১০,০০০ টাকা ডিপোজিট করতে পারবেন। সঠিক পরিমাণ দিন:", parse_mode="HTML")
                    return
                user_temp_deposit[user_id]["amount"] = amount
                user_temp_deposit[user_id]["step"] = "waiting_method"
                bot.send_message(user_id, f"{pe('sendmoney_shield')} <b>আপনি কিসের মাধ্যমে পেমেন্ট করতে চাচ্ছেন সিলেক্ট করুন:</b>", parse_mode="HTML", reply_markup=get_payment_method_markup())
                return
            except ValueError:
                bot.send_message(user_id, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 50 বা 500)।", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
                return

        elif state == "waiting_trx":
            user_temp_deposit[user_id]["trx_id"] = text.strip()
            user_temp_deposit[user_id]["step"] = "waiting_screenshot"
            bot.send_message(
                user_id,
                f"{pe('step_tick')} <b>ধন্যবাদ! আপনার ট্রানজেকশন আইডি গ্রহণ করা হয়েছে।</b>\n\n"
                f"{pe('camera_icon')} এখন পেমেন্টের একটি স্ক্রিনশট (Screenshot) এই চ্যাটে পাঠান:",
                parse_mode="HTML",
                reply_markup=get_permanent_keyboard(user_id)
            )
            return

        elif state == "waiting_service_username":
            data = user_temp_deposit[user_id]
            cat_id, sub_name, price, username_input = data["cat_id"], data["sub_name"], data["price"], text.strip()
            del user_temp_deposit[user_id]

            conn = sqlite3.connect("shop_bot.db", timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            bal_res = cursor.fetchone()
            current_bal = bal_res[0] if bal_res else 0.0

            if current_bal < price:
                conn.close()
                bot.send_message(user_id, f"{pe('insufficient_bal')} আপনার একাউন্টে পর্যাপ্ত ব্যালেন্স নেই!", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
                return

            new_bal = current_bal - price
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, user_id))
            conn.commit()
            conn.close()

            emoji_k = "telegram_premium_cat" if "telegram" in cat_id else get_vpn_emoji_key(sub_name)
            bot.send_message(
                user_id,
                f"{pe('order_pending')} আপনার অর্ডারটি সফলভাবে সাবমিট হয়েছে!\n\n"
                f"{pe(emoji_k)} সার্ভিস: <b>{sub_name}</b> {pe(emoji_k)}\n"
                f"{pe('profile_user')} ইউজারনেম/আইডি: <code>{username_input}</code>\n"
                f"{pe('money_spent')} পরিশোধিত মূল্য: ৳{price}\n"
                f"{pe('wallet_balance')} অবশিষ্ট ব্যালেন্স: ৳{new_bal}\n\n"
                f"{pe('waiting_clock')} দয়া করে কিছুক্ষণ অপেক্ষা করুন, অ্যাডমিন খুব শীঘ্রই আপনার সার্ভিসটি কমপ্লিট করে দেবেন।",
                parse_mode="HTML",
                reply_markup=get_permanent_keyboard(user_id)
            )

            admin_markup = InlineKeyboardMarkup()
            admin_markup.add(premium_inline_button("Complete Order & Deliver", "approve_btn", callback_data=f"complete_order_{user_id}"))

            admin_order_msg = (
                f"{pe('alarm_bell')} <b>New Order Received!</b>\n\n"
                f"{pe('profile_user')} <b>User ID:</b> <code>{user_id}</code>\n"
                f"{pe('box_package')} <b>Service:</b> <b>{sub_name}</b>\n"
                f"{pe('username_link')} <b>Target Account:</b> <code>{username_input}</code>\n"
                f"{pe('money_spent')} <b>Price:</b> ৳{price}"
            )
            bot.send_message(ADMIN_ID, admin_order_msg, parse_mode="HTML", reply_markup=admin_markup)
            return

        elif state == "waiting_custom_qty":
            cat_id = user_temp_deposit[user_id]["cat_id"]
            try:
                qty = int(text)
                if qty <= 0:
                    bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক পিস সংখ্যা লিখুন।", parse_mode="HTML")
                    return
                del user_temp_deposit[user_id]
                process_purchase(message.chat.id, user_id, cat_id, qty)
                return
            except ValueError:
                bot.reply_to(message, f"{pe('warn_icon')} দয়া করে শুধু সংখ্যা লিখে পাঠান।", parse_mode="HTML")
                return

    # অ্যাডমিন প্যানেল অ্যাকশনস
    if user_id == ADMIN_ID and user_id in admin_states:
        state_data = admin_states[user_id]
        action = state_data.get("action")

        if action == "adding_new_cat":
            parts = text.rsplit(maxsplit=1)
            if len(parts) == 2:
                name, price_str = parts[0], parts[1].replace('৳', '').strip()
                try:
                    price = float(price_str)
                    admin_states[user_id] = {"pending_btn_data": {"mode": "new_cat", "name": name, "price": price}}
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        premium_inline_button("Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                        premium_inline_button("No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                    bot.reply_to(message, f"<b>{name}</b> (৳{price})\n\nআপনি কি এই বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                    return
                except ValueError:
                    bot.reply_to(message, f"{pe('warn_icon')} দাম সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                    return

        elif action == "editing_cat":
            cat_id = state_data["cat_id"]
            parts = text.rsplit(maxsplit=1)
            if len(parts) == 2:
                name, price_str = parts[0], parts[1].replace('৳', '').strip()
                try:
                    price = float(price_str)
                    admin_states[user_id] = {"pending_btn_data": {"mode": "edit_cat", "cat_id": cat_id, "name": name, "price": price}}
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        premium_inline_button("Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                        premium_inline_button("No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                    bot.reply_to(message, f"<b>{name}</b> (৳{price})\n\nআপনি কি এই বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                    return
                except ValueError:
                    bot.reply_to(message, f"{pe('warn_icon')} দামটি সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                    return

        elif action == "adding_sub_item":
            cat_id = state_data["cat_id"]
            parts = text.rsplit(maxsplit=1)
            if len(parts) == 2:
                sub_name, price_str = parts[0], parts[1].replace('৳', '').strip()
                try:
                    price = float(price_str)
                    admin_states[user_id] = {"pending_btn_data": {"mode": "new_sub", "cat_id": cat_id, "name": sub_name, "price": price}}
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.add(
                        premium_inline_button("Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                        premium_inline_button("No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                    bot.reply_to(message, f"<b>{sub_name}</b> (৳{price})\n\nআপনি কি এই প্যাকেজ বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                    return
                except ValueError:
                    bot.reply_to(message, f"{pe('warn_icon')} দাম সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                    return

        elif action == "waiting_member_uid_for_balance":
            state_data["target_uid"] = text.strip()
            state_data["action"] = "waiting_member_amount_for_balance"
            bot.reply_to(message, f"{pe('deposit_money')} এখন এই ইউজারের অ্যাকাউন্টে কত টাকা ব্যাক দিতে চাচ্ছেন? সঠিক পরিমাণ (যেমন: <code>50</code> বা <code>0.09</code>) চ্যাটে লিখে পাঠান:", parse_mode="HTML")
            return

        elif action == "waiting_member_amount_for_balance":
            target_uid_str = state_data["target_uid"]
            del admin_states[user_id]
            try:
                target_uid = int(target_uid_str)
                add_amount = float(text.strip())

                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, balance FROM users WHERE user_id = ?", (target_uid,))
                user_row = cursor.fetchone()

                if user_row:
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (add_amount, target_uid))
                    conn.commit()
                    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,))
                    new_bal = cursor.fetchone()[0]
                else:
                    cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_uid, "User", add_amount))
                    conn.commit()
                    new_bal = add_amount
                conn.close()

                try:
                    bot.send_message(
                        target_uid,
                        f"{pe('deposit_success')} <b>বট আপডেট করা হয়েছে!</b>\n\nআপনার একাউন্টে পূর্বের পাওনা ৳{add_amount} টাকা এড করা হয়েছে। এখন আপনারা কেনাকাটা করতে পারেন!",
                        parse_mode="HTML",
                        reply_markup=get_permanent_keyboard(target_uid)
                    )
                except Exception:
                    pass

                bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজার (<code>{target_uid}</code>) এর অ্যাকাউন্টে ব্যালেন্স <b>৳{add_amount}</b> যোগ করা হয়েছে! নতুন ব্যালেন্স: ৳{new_bal}", parse_mode="HTML")
            except ValueError:
                bot.reply_to(message, f"{pe('warn_icon')} ইউজার আইডি অথবা টাকার পরিমাণ সঠিক সংখ্যায় দিন। পুনরায় অ্যাডমিন প্যানেল থেকে চেষ্টা করুন।", parse_mode="HTML")
            return

        elif action == "waiting_member_uid_for_remove_money":
            target_uid_str = text.strip()
            try:
                target_uid = int(target_uid_str)
                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                cursor.execute("SELECT balance, first_name FROM users WHERE user_id = ?", (target_uid,))
                row = cursor.fetchone()
                conn.close()

                if row:
                    current_bal = row[0]
                    u_name = row[1] or "User"
                    state_data["target_uid"] = target_uid
                    state_data["action"] = "waiting_member_amount_for_remove_money"
                    bot.reply_to(message, f"{pe('profile_user')} ইউজার: <b>{u_name}</b> (ID: <code>{target_uid}</code>)\nবর্তমান ব্যালেন্স: <b>৳{current_bal}</b>\n\nএখন আপনি ওনার অ্যাকাউন্টে কত টাকা রাখতে চাচ্ছেন (বা কত টাকা করতে চাচ্ছেন) সেটির সঠিক পরিমাণ চ্যাটে লিখে পাঠান:", parse_mode="HTML")
                else:
                    del admin_states[user_id]
                    bot.reply_to(message, f"{pe('warn_icon')} এই ইউজার আইডি দিয়ে ডাটাবেজে কোনো রেকর্ড পাওয়া যায়নি।", parse_mode="HTML")
            except ValueError:
                del admin_states[user_id]
                bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যায় ইউজার আইডি দিন।", parse_mode="HTML")
            return

        elif action == "waiting_member_amount_for_remove_money":
            target_uid = state_data["target_uid"]
            del admin_states[user_id]
            try:
                new_amount = float(text.strip())
                if new_amount < 0:
                    bot.reply_to(message, f"{pe('warn_icon')} টাকার পরিমাণ ঋণাত্মক হতে পারে না।", parse_mode="HTML")
                    return

                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_amount, target_uid))
                conn.commit()
                conn.close()

                try:
                    bot.send_message(
                        target_uid,
                        f"{pe('deposit_success')} <b>অ্যাকাউন্ট ব্যালেন্স আপডেট হয়েছে!</b>\n\nআপনার একাউন্টের বর্তমান ব্যালেন্স এডজাস্ট করে <b>৳{new_amount}</b> নির্ধারণ করা হয়েছে।",
                        parse_mode="HTML",
                        reply_markup=get_permanent_keyboard(target_uid)
                    )
                except Exception:
                    pass

                bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজার (<code>{target_uid}</code>)-এর অ্যাকাউন্ট ব্যালেন্স এডিট করে <b>৳{new_amount}</b> করা হয়েছে!", parse_mode="HTML")
            except ValueError:
                bot.reply_to(message, f"{pe('warn_icon')} টাকার পরিমাণ সঠিক সংখ্যায় দিন।", parse_mode="HTML")
            return

        elif action == "searching_user":
            del admin_states[user_id]
            target_id_str = text.strip()
            try:
                target_uid = int(target_id_str)
                conn = sqlite3.connect("shop_bot.db", timeout=30)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, first_name, balance, username FROM users WHERE user_id = ?", (target_uid,))
                user_row = cursor.fetchone()
                conn.close()
                if user_row:
                    u_id, u_name, u_bal, u_user = user_row
                    resp = (
                        f"{pe('profile_user')} <b>User Profile & Details:</b>\n\n"
                        f"{pe('profile_user')} <b>Name:</b> {u_name or 'User'}\n"
                        f"{pe('username_link')} <b>Username:</b> <b>{u_user or 'N/A'}</b>\n"
                        f"{pe('id_badge')} <b>User ID:</b> <code>{u_id}</code>\n"
                        f"{pe('balance_coin')} <b>Account Balance:</b> <b>৳{u_bal}</b> {pe('diamond_badge')}"
                    )
                    bot.reply_to(message, resp, parse_mode="HTML")
                else:
                    bot.reply_to(message, f"{pe('warn_icon')} এই ইউজার আইডি দিয়ে কোনো রেকর্ড পাওয়া যায়নি।", parse_mode="HTML")
            except ValueError:
                bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যায় ইউজার আইডি দিন।", parse_mode="HTML")
            return

        elif action == "waiting_delivery_content":
            target_user = state_data["target_user"]
            del admin_states[user_id]
            try:
                bot.send_message(target_user, f"{pe('order_delivered')} <b>আপনার অর্ডারটি সফলভাবে সম্পন্ন হয়েছে!</b>\n\n{pe('box_package')} <b>ডিটেইলস / অ্যাকাউন্ট:</b>\n{text}\n\nআমাদের সাথে থাকার জন্য ধন্যবাদ! {pe('welcome_heart')}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
                bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজারের কাছে (ID: <code>{target_user}</code>) অর্ডার ডেলিভারি পাঠানো হয়েছে!", parse_mode="HTML")
            except Exception as e:
                bot.reply_to(message, f"ইউজারের কাছে মেসেজ পাঠানো যায়নি: {e}")
            return

# ----------------- Web Server & Polling -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    def run_bot():
        while True:
            try:
                bot.remove_webhook()
                bot.infinity_polling(none_stop=True, interval=0, timeout=20, long_polling_timeout=20)
            except Exception as e:
                print(f"Polling crashed: {e}")
                time.sleep(1)
        
    t_bot = threading.Thread(target=run_bot)
    t_bot.start()
    
    t_backup = threading.Thread(target=auto_drive_backup_loop, daemon=True)
    t_backup.start()
    
    app.run(host="0.0.0.0", port=port)
