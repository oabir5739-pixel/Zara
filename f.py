# -*- coding: utf-8 -*-
[cite: 1]import os
[cite: 1]import sqlite3
[cite: 1]import threading
[cite: 1]import time
[cite: 1]import html
[cite: 1]from flask import Flask
[cite: 1]import telebot
[cite: 1]from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
[cite: 1]import uuid
[cite: 1]import re
[cite: 1]from google.oauth2 import service_account
[cite: 1]from googleapiclient.discovery import build
[cite: 1]from googleapiclient.http import MediaFileUpload

# 🔑 টোকেন এবং অ্যাডমিন আইডি
[cite: 1]TOKEN = "8950372563:AAHDH5hPsjJfQknZAUFn9v5-W7jgWE3oMqc"
[cite: 1]ADMIN_ID = 7196917072

[cite: 1]FORCE_SUB_CHANNEL = "@BotAllUpdateServis"

[cite: 1]bot = telebot.TeleBot(TOKEN)
[cite: 1]user_temp_deposit = {}
[cite: 1]pending_deposits = {}
[cite: 1]admin_states = {}
[cite: 1]order_delivery_cache = {}

# ----------------- Premium Custom Emoji Config (Buttons) -----------------
[cite: 1]PREMIUM_EMOJIS = {
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
    "remove_money": "6068810023566317366",
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

[cite: 1]POST_PREMIUM_EMOJIS = {
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

[cite: 1]def pe(key):
   [cite: 1]emoji_id = POST_PREMIUM_EMOJIS.get(key, "")
   [cite: 1]if emoji_id:
       [cite: 1]return f'<tg-emoji emoji-id="{emoji_id}">✨</tg-emoji>'
   [cite: 1]return ""

[cite: 1]def get_vpn_emoji_key(vpn_name):
   [cite: 1]low = vpn_name.lower()
   [cite: 1]if "nord" in low: return "vpn_nord"
   [cite: 1]if "express" in low: return "vpn_express"
   [cite: 1]if "ipvanish" in low: return "vpn_ipvanish"
   [cite: 1]if "hma" in low: return "vpn_hma"
   [cite: 1]if "x vpn" in low or "x-vpn" in low: return "vpn_xvpn"
   [cite: 1]if "proton" in low: return "vpn_proton"
   [cite: 1]return "vpn_service_cat"

[cite: 1]OWNER_PREMIUM_SETTING = "owner_premium"

[cite: 1]def update_owner_premium_status(user):
   [cite: 1]if not user or user.id != ADMIN_ID: return
   [cite: 1]premium = getattr(user, "is_premium", None)
   [cite: 1]if premium is None: return
   [cite: 1]try:
       [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
       [cite: 1]cursor = conn.cursor()
       [cite: 1]cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (OWNER_PREMIUM_SETTING, "1" if premium else "0"))
       [cite: 1]conn.commit()
       [cite: 1]conn.close()
   [cite: 1]except Exception:
       [cite: 1]pass

[cite: 1]def owner_has_premium():
   [cite: 1]try:
       [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
       [cite: 1]cursor = conn.cursor()
       [cite: 1]cursor.execute("SELECT value FROM settings WHERE key = ?", (OWNER_PREMIUM_SETTING,))
       [cite: 1]row = cursor.fetchone()
       [cite: 1]conn.close()
       [cite: 1]return bool(row and row[0] == "1")
    [cite: 1]except Exception:
       [cite: 1]return False

[cite: 1]def premium_keyboard_button(text, emoji_key):
   [cite: 1]emoji_id = PREMIUM_EMOJIS.get(emoji_key)
   [cite: 1]if owner_has_premium() and emoji_id:
       [cite: 1]return KeyboardButton(text, icon_custom_emoji_id=emoji_id)
   [cite: 1]return KeyboardButton(text)

# ইনলাইন বাটনে যাতে কোনো সমস্যা না হয়, তাই সরাসরি টেক্সটের সাথে ইউনিকোড ইমোজি সেট করে দেওয়া হলো
[cite: 1]def premium_inline_button(text, emoji_key, callback_data=None, url=None):
   [cite: 1]kwargs = {}
   [cite: 1]if callback_data is not None: kwargs["callback_data"] = callback_data
   [cite: 1]if url is not None: kwargs["url"] = url
   [cite: 1]return InlineKeyboardButton(text, **kwargs)

[cite: 1]USER_LOG_FILE = "auto_member_count_user.txt"

[cite: 1]def save_user_id_to_file(user_id):
   [cite: 1]try:
       [cite: 1]existing_ids = set()
       [cite: 1]if os.path.exists(USER_LOG_FILE):
            [cite: 1]with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
               [cite: 1]existing_ids = {line.strip() for line in f if line.strip()}
       [cite: 1]if str(user_id) not in existing_ids:
           [cite: 1]with open(USER_LOG_FILE, "a", encoding="utf-8") as f:
               [cite: 1]f.write(f"{user_id}\n")
    [cite: 1]except Exception:
       [cite: 1]pass

[cite: 1]def check_user_subscription(user_id):
   [cite: 1]if ADMIN_ID and user_id == ADMIN_ID: return True
   [cite: 1]try:
       [cite: 1]member = bot.get_chat_member(FORCE_SUB_CHANNEL, user_id)
       [cite: 1]if member.status in ['member', 'administrator', 'creator']: return True
   [cite: 1]except Exception:
       [cite: 1]pass
   [cite: 1]return False

[cite: 1]def get_force_sub_markup():
   [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
   [cite: 1]markup.add(
       [cite: 1]premium_inline_button("🔗 Join Channel", "channel_join", url=f"https://t.me/BotAllUpdateServis"),
       [cite: 1]premium_inline_button("✅ Verify", "verify_tick", callback_data="verify_subscription")
    )
   [cite: 1]return markup

[cite: 1]def get_deposit_amount_markup():
   [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
   [cite: 1]markup.add(
       [cite: 1]premium_inline_button("💵 10 টাকা", "money_10", callback_data="depamt_10"),
       [cite: 1]premium_inline_button("💵 20 টাকা", "money_20", callback_data="depamt_20"),
       [cite: 1]premium_inline_button("💵 30 টাকা", "money_30", callback_data="depamt_30"),
       [cite: 1]premium_inline_button("💵 40 টাকা", "money_40", callback_data="depamt_40")
    )
   [cite: 1]return markup

[cite: 1]def get_payment_method_markup():
   [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
   [cite: 1]markup.add(
       [cite: 1]premium_inline_button("💳 bKash", "bkash", callback_data="paymethod_bKash"),
       [cite: 1]premium_inline_button("💳 Nagad", "nagad", callback_data="paymethod_Nagad"),
       [cite: 1]premium_inline_button("💳 Rocket", "rocket", callback_data="paymethod_Rocket")
    )
   [cite: 1]return markup

[cite: 1]def auto_drive_backup_loop():
   [cite: 1]SCOPES = ['https://www.googleapis.com/auth/drive.file']
   [cite: 1]SERVICE_ACCOUNT_FILE = 'credentials.json' 
   [cite: 1]PARENT_FOLDER_ID = '1Fmf22X9PIWhi1qH5q1pf_4xWGeDOMH6V' 

   [cite: 1]while True:
       [cite: 1]time.sleep(86400) 
       [cite: 1]try:
           [cite: 1]if not os.path.exists('shop_bot.db'): continue
           [cite: 1]creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
           [cite: 1]service = build('drive', 'v3', credentials=creds)
           [cite: 1]query = f"name = 'shop_bot.db' and '{PARENT_FOLDER_ID}' in parents and trashed = false"
           [cite: 1]response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
           [cite: 1]files = response.get('files', [])
           [cite: 1]media = MediaFileUpload('shop_bot.db', resumable=True)
           [cite: 1]if files:
               [cite: 1]service.files().update(fileId=files[0]['id'], media_body=media).execute()
           [cite: 1]else:
               [cite: 1]service.files().create(body={'name': 'shop_bot.db', 'parents': [PARENT_FOLDER_ID]}, media_body=media, fields='id').execute()
       [cite: 1]except Exception:
           [cite: 1]pass

[cite: 1]def init_db():
   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        balance REAL DEFAULT 0.0,
                        username TEXT
                    )''')
   [cite: 1]try: cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
   [cite: 1]except sqlite3.OperationalError: pass
   [cite: 1]try: cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
   [cite: 1]except sqlite3.OperationalError: pass

    [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
                        cat_id TEXT PRIMARY KEY,
                        name TEXT,
                        price REAL,
                        has_emoji INTEGER DEFAULT 1,
                        group_type TEXT DEFAULT 'mail'
                    )''')
   [cite: 1]try: cursor.execute("ALTER TABLE categories ADD COLUMN has_emoji INTEGER DEFAULT 1")
   [cite: 1]except sqlite3.OperationalError: pass
   [cite: 1]try: cursor.execute("ALTER TABLE categories ADD COLUMN group_type TEXT DEFAULT 'mail'")
   [cite: 1]except sqlite3.OperationalError: pass

    [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS sub_services (
                        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cat_id TEXT,
                        sub_name TEXT,
                        price REAL,
                        has_emoji INTEGER DEFAULT 1
                    )''')
   [cite: 1]try: cursor.execute("ALTER TABLE sub_services ADD COLUMN has_emoji INTEGER DEFAULT 1")
   [cite: 1]except sqlite3.OperationalError: pass

   [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS stock (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cat_id TEXT,
                        content TEXT
                    )''')
   [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS custom_buttons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        btn_name TEXT,
                        btn_url TEXT
                    )''')
   [cite: 1]cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )''')
   [cite: 1]conn.commit()

   [cite: 1]default_posts = {
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

   [cite: 1]for key, val in default_posts.items():
       [cite: 1]cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, val))
   [cite: 1]conn.commit()

   [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES ('hotmail', 'Hotmail Account', 0.85, 1, 'mail')")
    [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES ('outlook', 'Outlook Account', 0.85, 1, 'mail')")
   [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES ('Outlook fr', 'Outlook fr. (High quality)', 1.0, 1, 'mail')")
   [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES ('Ig Hotmail', 'Instagram Id Create Hotmail', 0.55, 1, 'mail')")
   [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES ('proxy', 'Owl Proxy (200MB)', 7.0, 1, 'proxy')")

   [cite: 1]cursor.execute("SELECT COUNT(*) FROM sub_services WHERE cat_id = 'telegram_premium'")
   [cite: 1]if cursor.fetchone()[0] == 0:
       [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (3 Month)', 2010.0, 1)")
       [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (6 Month)', 2520.0, 1)")
       [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('telegram_premium', 'Telegram Premium (12 Month)', 4030.0, 1)")

   [cite: 1]cursor.execute("SELECT COUNT(*) FROM sub_services WHERE cat_id LIKE 'vpn_%'")
   [cite: 1]if cursor.fetchone()[0] == 0:
       [cite: 1]vpns = ["Nord VPN", "Express VPN", "IPVanish VPN", "Hma VPN", "X VPN", "Proton VPN"]
       [cite: 1]for v in vpns:
           [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_3d', ?, 20.0, 1)", (f"{v} (3 Day)",))
           [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_7d', ?, 35.0, 1)", (f"{v} (7 Day)",))
           [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_9d', ?, 45.0, 1)", (f"{v} (9 Day)",))
           [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES ('vpn_1m', ?, 95.0, 1)", (f"{v} (1 Month)",))

   [cite: 1]conn.commit()
   [cite: 1]conn.close()

[cite: 1]init_db()

[cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
[cite: 1]cursor = conn.cursor()
[cite: 1]cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (OWNER_PREMIUM_SETTING, "0"))
[cite: 1]conn.commit()
[cite: 1]conn.close()

[cite: 1]def get_setting_msg(key, default=""):
   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
   [cite: 1]res = cursor.fetchone()
   [cite: 1]conn.close()
   [cite: 1]return res[0] if res else default

[cite: 1]def get_permanent_keyboard(user_id):
   [cite: 1]markup = ReplyKeyboardMarkup(resize_keyboard=True)
   [cite: 1]markup.row(
       [cite: 1]premium_keyboard_button("All Services", "all_services"),
       [cite: 1]premium_keyboard_button("Deposit", "deposit")
    )
   [cite: 1]markup.row(
       [cite: 1]premium_keyboard_button("Profile", "profile"),
       [cite: 1]premium_keyboard_button("Support", "support")
    )
   [cite: 1]if user_id == ADMIN_ID:
       [cite: 1]markup.row(
           [cite: 1]premium_keyboard_button("Admin Panel", "admin_panel"),
           [cite: 1]premium_keyboard_button("Search User ID", "search_user")
        )
   [cite: 1]markup.row(premium_keyboard_button("Restart Bot", "restart"))
   [cite: 1]return markup

[cite: 1]def main_menu_inline(user_id):
   [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
    [cite: 1]cursor.execute("SELECT btn_name, btn_url FROM custom_buttons")
   [cite: 1]custom_btns = cursor.fetchall()
   [cite: 1]conn.close()
   [cite: 1]for b_name, b_url in custom_btns:
       [cite: 1]markup.add(premium_inline_button(b_name, "home_button", url=b_url))
   [cite: 1]return markup

# ইনলাইন বাটনগুলোতে সরাসরি ইউনিকোড ইমোজি যুক্ত করা হয়েছে
[cite: 1]def get_categories_markup():
   [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
   [cite: 1]markup.add(
       [cite: 1]premium_inline_button("✉️ All Mail Service", "mail_cat", callback_data="group_mail"),
       [cite: 1]premium_inline_button("🌐 All Proxy Service", "proxy_cat", callback_data="group_proxy"),
       [cite: 1]premium_inline_button("💎 Telegram Premium Buy", "telegram_premium_cat", callback_data="special_cat_telegram_premium"),
       [cite: 1]premium_inline_button("🛡️ VPN Service", "vpn_service_cat", callback_data="special_cat_vpn_service")
    )
   [cite: 1]return markup

[cite: 1]def get_admin_markup():
   [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
   [cite: 1]markup.add(
       [cite: 1]premium_inline_button("📊 Bot Analytics & Users", "analytics", callback_data="admin_analytics"),
       [cite: 1]premium_inline_button("📁 Auto Count Member ID", "member_count_file", callback_data="admin_auto_member_count"),
       [cite: 1]premium_inline_button("💰 All Member Balance List", "balance_list", callback_data="admin_member_balance_list"),
        [cite: 1]premium_inline_button("📥 Download Balance List TXT", "download_txt", callback_data="admin_download_balance_txt"),
       [cite: 1]premium_inline_button("🔄 Recover Balance List (.txt)", "recover_balance", callback_data="admin_recover_balance_list"),
       [cite: 1]premium_inline_button("📢 Live Analysis & User Broadcast Message", "live_broadcast", callback_data="admin_live_broadcast"),
       [cite: 1]premium_inline_button("➕ Add Member Money Back", "add_balance", callback_data="admin_add_member_balance"),
       [cite: 1]premium_inline_button("❌ Remove Money", "remove_money", callback_data="admin_remove_member_balance"),
       [cite: 1]premium_inline_button("🔄 Update Back All Money Member", "bulk_update", callback_data="admin_bulk_money_update"),
       [cite: 1]premium_inline_button("✏️ All Post Edit", "post_edit", callback_data="admin_all_post_edit"),
       [cite: 1]premium_inline_button("📝 All Button Edit", "button_edit", callback_data="admin_all_button_edit"),
       [cite: 1]premium_inline_button("⚙️ Edit Prices & Services", "edit_service", callback_data="admin_edit_services"),
       [cite: 1]premium_inline_button("📦 Manage Stock (Add/Remove)", "manage_stock", callback_data="admin_add_stock_menu")
    )
   [cite: 1]return markup

[cite: 1]@bot.message_handler(func=lambda message: message.text and "Restart Bot" in message.text)
[cite: 1]@bot.message_handler(commands=['start'])
[cite: 1]def send_welcome(message):
   [cite: 1]update_owner_premium_status(message.from_user)
   [cite: 1]user_id = message.from_user.id
   [cite: 1]first_name = message.from_user.first_name or "User"
   [cite: 1]username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
   [cite: 1]save_user_id_to_file(user_id)

   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
   [cite: 1]existing_user = cursor.fetchone()
   [cite: 1]if not existing_user:
       [cite: 1]cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, 0.0, ?)", (user_id, first_name, username))
   [cite: 1]else:
       [cite: 1]cursor.execute("UPDATE users SET first_name = ?, username = ? WHERE user_id = ?", (first_name, username, user_id))
   [cite: 1]conn.commit()
   [cite: 1]conn.close()

   [cite: 1]if not check_user_subscription(user_id):
       [cite: 1]not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি আমাদের চ্যানেলে Join করেননি!")
       [cite: 1]bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
       [cite: 1]return

   [cite: 1]welcome_template = get_setting_msg('welcome_msg', f"স্বাগতম {{first_name}}!")
   [cite: 1]landing_text = welcome_template.replace("{first_name}", first_name)

   [cite: 1]bot.send_message(message.chat.id, landing_text, parse_mode="HTML", reply_markup=main_menu_inline(user_id))
   [cite: 1]bot.send_message(message.chat.id, f"{pe('down_arrow')} আপনার সুবিধার্থে নিচের মেনু বাটনগুলো ব্যবহার করুন:", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))

[cite: 1]@bot.message_handler(func=lambda message: message.text and any(keyword in message.text for keyword in ["All Services", "Deposit", "Profile", "Support", "Admin Panel", "Search User ID"]))
[cite: 1]def handle_reply_buttons(message):
   [cite: 1]update_owner_premium_status(message.from_user)
   [cite: 1]user_id = message.from_user.id
   [cite: 1]text = message.text
   [cite: 1]username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
   [cite: 1]save_user_id_to_file(user_id)

   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
   [cite: 1]conn.commit()
   [cite: 1]conn.close()

   [cite: 1]if not check_user_subscription(user_id):
       [cite: 1]not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি এখনো চ্যানেলে Join করেননি!")
       [cite: 1]bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
       [cite: 1]return

   [cite: 1]if user_id in user_temp_deposit:
       [cite: 1]del user_temp_deposit[user_id]
    
   [cite: 1]if "All Services" in text:
       [cite: 1]markup = get_categories_markup()
       [cite: 1]bot.send_message(message.chat.id, f"{pe('welcome_shop')} <b>আমাদের কাছে নিচের সার্ভিসগুলো রয়েছে:</b>", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif "Deposit" in text:
       [cite: 1]user_temp_deposit[user_id] = {"step": "waiting_amount"}
       [cite: 1]msg = get_setting_msg('deposit_info_msg', (
           [cite: 1]f"{pe('deposit_money')} <b>আপনি কত টাকা ডিপোজিট করতে চান সংখ্যাটি লিখে পাঠান:</b>\n\n"
           [cite: 1]f"{pe('list_point')} সর্বনিম্ন ১০ টাকা\n"
           [cite: 1]f"{pe('list_point')} সর্বোচ্চ ১০০০০ টাকা"
        ))
       [cite: 1]bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=get_deposit_amount_markup())

   [cite: 1]elif "Profile" in text:
       [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
       [cite: 1]cursor = conn.cursor()
       [cite: 1]cursor.execute("SELECT balance, username FROM users WHERE user_id = ?", (user_id,))
       [cite: 1]res = cursor.fetchone()
       [cite: 1]bal = res[0] if res else 0.0
       [cite: 1]u_name = res[1] if res and res[1] else username
       [cite: 1]conn.close()
        
       [cite: 1]profile_text = (
           [cite: 1]f"{pe('profile_user')} <b>Your Account Profile</b>\n\n"
           [cite: 1]f"{pe('id_badge')} <b>User ID:</b> <code>{user_id}</code>\n"
           [cite: 1]f"{pe('username_link')} <b>Username:</b> <b>{u_name}</b>\n"
            [cite: 1]f"{pe('balance_coin')} <b>Account Balance:</b> <b>৳{bal}</b> {pe('diamond_badge')}"
        )
       [cite: 1]bot.send_message(message.chat.id, profile_text, parse_mode="HTML")

   [cite: 1]elif "Support" in text:
       [cite: 1]supp_msg = get_setting_msg('support_msg', f"{pe('support_headphone')} যেকোনো প্রয়োজনে আমাদের সাপোর্ট আইডিতে যোগাযোগ করুন:\nhttps://t.me/FBbuysellAX")
       [cite: 1]bot.send_message(message.chat.id, supp_msg, parse_mode="HTML")

   [cite: 1]elif "Search User ID" in text and user_id == ADMIN_ID:
       [cite: 1]admin_states[user_id] = {"action": "searching_user"}
       [cite: 1]bot.send_message(message.chat.id, f"{pe('list_point')} ইউজারের সম্পূর্ণ তথ্য ও ব্যালেন্স দেখতে তার <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML")

   [cite: 1]elif "Admin Panel" in text and user_id == ADMIN_ID:
       [cite: 1]bot.send_message(message.chat.id, f"{pe('admin_crown')} <b>Admin Control Panel</b>\n\nনিচের অপশনগুলো থেকে ম্যানেজ করুন:", parse_mode="HTML", reply_markup=get_admin_markup())

[cite: 1]def process_purchase(chat_id, user_id, cat_id, qty):
   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("SELECT price, name FROM categories WHERE cat_id = ?", (cat_id,))
   [cite: 1]cat_data = cursor.fetchone()
   [cite: 1]if not cat_data:
       [cite: 1]conn.close()
       [cite: 1]bot.send_message(chat_id, f"{pe('warn_icon')} এই সার্ভিসটি বর্তমানে আর উপলব্ধ নেই।", parse_mode="HTML")
       [cite: 1]return

   [cite: 1]price_per_item = cat_data[0]
   [cite: 1]cat_name = cat_data[1]
   [cite: 1]total_cost = price_per_item * qty

   [cite: 1]cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
   [cite: 1]user_balance_row = cursor.fetchone()
    [cite: 1]user_balance = user_balance_row[0] if user_balance_row else 0.0

   [cite: 1]if user_balance < total_cost:
        [cite: 1]conn.close()
       [cite: 1]bot.send_message(
           [cite: 1]chat_id, 
           [cite: 1]f"{pe('insufficient_bal')} <b>আপনার অ্যাকাউন্টে পর্যাপ্ত ব্যালেন্স নেই!</b>\n\n"
           [cite: 1]f"{pe('money_spent')} প্রয়োজন: ৳{total_cost}\n"
           [cite: 1]f"{pe('wallet_balance')} আপনার আছে: ৳{user_balance}\n\n"
           [cite: 1]f"{pe('step_tick')} আগে ডিপোজিট করুন, তারপর পণ্য কিনুন।",
           [cite: 1]parse_mode="HTML",
           [cite: 1]reply_markup=get_permanent_keyboard(user_id)
        )
       [cite: 1]return

   [cite: 1]cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
   [cite: 1]stock_count = cursor.fetchone()[0]

   [cite: 1]if stock_count < qty:
        [cite: 1]conn.close()
       [cite: 1]bot.send_message(chat_id, f"{pe('no_stock')} দুঃখিত, এই মুহূর্তে পর্যাপ্ত স্টক নেই! স্টকে আছে: <b>{stock_count} পিস</b>።", parse_mode="HTML")
       [cite: 1]return

   [cite: 1]cursor.execute("SELECT id, content FROM stock WHERE cat_id = ? ORDER BY id ASC LIMIT ?", (cat_id, qty))
   [cite: 1]items = cursor.fetchall()

   [cite: 1]new_balance = user_balance - total_cost
   [cite: 1]cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))

   [cite: 1]for item_id, content in items:
       [cite: 1]cursor.execute("DELETE FROM stock WHERE id = ?", (item_id,))
    
   [cite: 1]conn.commit()
   [cite: 1]conn.close()

   [cite: 1]raw_contents = [content.strip() for item_id, content in items]
   [cite: 1]order_key = str(uuid.uuid4())[:8]
   [cite: 1]order_delivery_cache[order_key] = {
       [cite: 1]"items": raw_contents,
        [cite: 1]"cat_name": cat_name,
       [cite: 1]"qty": qty,
       [cite: 1]"cat_id": cat_id
    }

   [cite: 1]delivery_markup = InlineKeyboardMarkup(row_width=2)
   [cite: 1]delivery_markup.add(
       [cite: 1]premium_inline_button("📂 Open Here", "open_here_btn", callback_data=f"show_open_{order_key}"),
       [cite: 1]premium_inline_button("📄 TXT File", "txt_file_btn", callback_data=f"show_txt_{order_key}")
    )

   [cite: 1]purchase_msg = (
       [cite: 1]f"{pe('buy_success')} <b>Purchase Successful!</b>\n\n"
       [cite: 1]f"{pe('box_package')} Item: <b>{cat_name}</b>\n"
       [cite: 1]f"{pe('quantity_icon')} Quantity: <b>{qty} Pcs</b>\n"
       [cite: 1]f"{pe('money_spent')} Total Cost: <b>৳{total_cost}</b>\n"
       [cite: 1]f"{pe('wallet_balance')} Remaining Balance: <b>৳{new_balance}</b>\n\n"
       [cite: 1]f"{pe('choose_select')} <b>আপনার ফাইলটি বট থেকে নিতে চাচ্ছেন নাকি TXT ফাইল আকারে নিতে চাচ্ছেন সিলেক্ট করুন:</b>"
    )

   [cite: 1]bot.send_message(chat_id, purchase_msg, parse_mode="HTML", reply_markup=delivery_markup)

# ----------------- Callbacks & Handlers -----------------
[cite: 1]@bot.callback_query_handler(func=lambda call: True)
[cite: 1]def handle_callback(call):
   [cite: 1]update_owner_premium_status(call.from_user)
   [cite: 1]user_id = call.from_user.id
   [cite: 1]username = f"@{call.from_user.username}" if call.from_user.username else "N/A"
   [cite: 1]save_user_id_to_file(user_id)

   [cite: 1]if call.data.startswith("show_open_"):
        [cite: 1]order_key = call.data.replace("show_open_", "")
       [cite: 1]if order_key in order_delivery_cache:
           [cite: 1]data = order_delivery_cache[order_key]
           [cite: 1]items = data["items"]
           [cite: 1]cat_name = data["cat_name"]
           [cite: 1]formatted_items = [f"{idx}. <code>{content}</code>" for idx, content in enumerate(items, 1)]
           [cite: 1]open_msg = f"{pe('buy_success')} <b>{cat_name} (Total: {len(items)} Pcs)</b>\n\n{pe('copy_down')} <b>ক্লিক করে কপি করুন:</b>\n\n" + "\n\n".join(formatted_items)
           [cite: 1]bot.send_message(call.message.chat.id, open_msg, parse_mode="HTML")
           [cite: 1]bot.answer_callback_query(call.id, "অ্যাকাউন্টগুলো নিচে ওপেন হয়েছে!")
       [cite: 1]else:
           [cite: 1]bot.answer_callback_query(call.id, "এই অর্ডারের সেশনটি মেয়াদোত্তীর্ণ হয়ে গেছে।", show_alert=True)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("show_txt_"):
       [cite: 1]order_key = call.data.replace("show_txt_", "")
       [cite: 1]if order_key in order_delivery_cache:
           [cite: 1]data = order_delivery_cache[order_key]
           [cite: 1]items, cat_name, cat_id = data["items"], data["cat_name"], data["cat_id"]
           [cite: 1]file_path = f"{cat_id}_order.txt"
           [cite: 1]with open(file_path, "w", encoding="utf-8") as f:
                [cite: 1]f.write("\n".join(items))
           [cite: 1]with open(file_path, "rb") as f:
               [cite: 1]bot.send_document(call.message.chat.id, f, caption=f"{pe('txt_file_caption')} <b>{cat_name}</b> এর টেক্সট ফাইল নিচে দেওয়া হলো:", parse_mode="HTML")
           [cite: 1]os.remove(file_path)
           [cite: 1]bot.answer_callback_query(call.id, "ফাইল পাঠানো হয়েছে!")
       [cite: 1]else:
           [cite: 1]bot.answer_callback_query(call.id, "এই অর্ডারের সেশনটি মেয়াদোত্তীর্ণ হয়ে গেছে।", show_alert=True)
        [cite: 1]return

   [cite: 1]if call.data == "verify_subscription":
       [cite: 1]if check_user_subscription(user_id):
           [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
            [cite: 1]cursor = conn.cursor()
           [cite: 1]cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
           [cite: 1]if not cursor.fetchone():
               [cite: 1]cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, 0.0, ?)", (user_id, call.from_user.first_name or "User", username))
           [cite: 1]else:
                [cite: 1]cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
           [cite: 1]conn.commit()
           [cite: 1]conn.close()

           [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
           [cite: 1]except Exception: pass

           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('step_tick')} আপনার একাউন্ট সফলভাবে Verify হয়েছে!\nএখন আপনি বটের সকল ফিচার ও কেনাকাটা করতে পারবেন। নিচে আপনার মেনু দেওয়া হলো:", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
       [cite: 1]else:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} আপনি এখনো চ্যানেলে Join করেননি! আগে চ্যানেলে জয়েন করুন তারপর Verify ক্লিক করুন।", parse_mode="HTML")
       [cite: 1]return

    [cite: 1]if not check_user_subscription(user_id):
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} আগে আমাদের চ্যানেলে Join করুন এবং Verify করুন!", parse_mode="HTML", reply_markup=get_force_sub_markup())
       [cite: 1]return

   [cite: 1]if call.data.startswith("depamt_"):
       [cite: 1]amt = float(call.data.split("_")[1])
       [cite: 1]user_temp_deposit[user_id] = {"amount": amt, "step": "waiting_method"}
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('sendmoney_shield')} <b>আপনি কিসের মাধ্যমে পেমেন্ট করতে চাচ্ছেন সিলেক্ট করুন:</b>", parse_mode="HTML", reply_markup=get_payment_method_markup())
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]return

   [cite: 1]if call.data.startswith("paymethod_"):
       [cite: 1]method = call.data.split("_")[1]
        [cite: 1]amt = user_temp_deposit.get(user_id, {}).get("amount", 10.0)
       [cite: 1]user_temp_deposit[user_id] = {
           [cite: 1]"amount": amt,
           [cite: 1]"method": method,
           [cite: 1]"step": "waiting_trx"
        }
       [cite: 1]number_map = {"bKash": "+8801842145918", "Nagad": "+8801842145918", "Rocket": "+8801842145918"}
       [cite: 1]pay_num = number_map.get(method, "+8801842145918")
       [cite: 1]method_pe_key = "bkash_method" if method == "bKash" else ("nagad_method" if method == "Nagad" else "rocket_method")

       [cite: 1]msg = (
           [cite: 1]f"{pe(method_pe_key)} আপনি <b>{method}</b> সিলেক্ট করেছেন।\n\n"
           [cite: 1]f"{pe('sendmoney_shield')} পার্সোনাল নাম্বারে টাকা সেন্ড মানি করুন:\n"
           [cite: 1]f"{pe(method_pe_key)} {method}: <code>{pay_num}</code>\n\n"
           [cite: 1]f"{pe('deposit_money')} <b>{int(amt) if amt.is_integer() else amt} TK Send Money</b>\n\n"
           [cite: 1]f"{pe('trx_input')} টাকা পাঠানোর পর আপনার ট্রানজেকশন আইডি (Transaction ID) চ্যাটে লিখে পাঠান:"
        )
       [cite: 1]bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
        [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]return

   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()

   [cite: 1]if call.data == "admin_main":
       [cite: 1]if user_id in admin_states: del admin_states[user_id]
       [cite: 1]conn.close()
        [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('admin_crown')} <b>Admin Control Panel</b>\n\nনিচের অপশনগুলো থেকে ম্যানেজ করুন:", parse_mode="HTML", reply_markup=get_admin_markup())
       [cite: 1]return

   [cite: 1]elif call.data == "admin_auto_member_count" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT user_id FROM users")
       [cite: 1]db_users = cursor.fetchall()
       [cite: 1]conn.close()
        
       [cite: 1]all_unique_ids = set()
       [cite: 1]for u in db_users:
           [cite: 1]all_unique_ids.add(str(u[0]))
            
       [cite: 1]if os.path.exists(USER_LOG_FILE):
           [cite: 1]with open(USER_LOG_FILE, "r", encoding="utf-8") as f:
               [cite: 1]for line in f:
                   [cite: 1]cleaned = line.strip()
                   [cite: 1]if cleaned: all_unique_ids.add(cleaned)
                    
       [cite: 1]with open(USER_LOG_FILE, "w", encoding="utf-8") as f:
           [cite: 1]for uid in sorted(all_unique_ids):
               [cite: 1]f.write(f"{uid}\n")
                
       [cite: 1]if all_unique_ids:
           [cite: 1]with open(USER_LOG_FILE, "rb") as f:
                [cite: 1]bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} <b>auto_member_count_user.txt</b>\nমোট মেম্বার সংখ্যা: <b>{len(all_unique_ids)} জন</b>", parse_mode="HTML")
           [cite: 1]bot.answer_callback_query(call.id, "ফাইল পাঠানো হয়েছে!")
       [cite: 1]else:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এখনো কোনো মেম্বারের ইউজার আইডি সেভ হয়নি।", parse_mode="HTML")
       [cite: 1]return

   [cite: 1]elif call.data == "admin_live_broadcast" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_analysis_txt_for_broadcast"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
        [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('loudspeaker')} <b>Live Analysis & User Broadcast Message</b>\n\nবট এনালাইসিস বা <code>auto_member_count_user.txt</code> ফাইলটি সরাসরি এখানে ফাইল আকারে পাঠান:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data == "admin_add_member_balance" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_member_uid_for_balance"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('add_balance')} <b>Add Member Money Back</b>\n\nযে ইউজারের অ্যাকাউন্টে আগের টাকা ব্যাক দিতে চাচ্ছেন, তার সঠিক <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data == "admin_remove_member_balance" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_member_uid_for_remove_money"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('remove_money')} <b>Remove Money (Balance Adjust)</b>\n\nযে ইউজারের অ্যাকাউন্ট থেকে টাকা কাট বা এডিট করতে চান, তার সঠিক <b>User ID</b> চ্যাটে লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data == "admin_bulk_money_update" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_bulk_money_data"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('bulk_update')} <b>Update Back All Money Member (Bulk Update)</b>\n\nআপনার আগের ডাউনলোড করা <code>all_member_balance_list.txt</code> ফাইলটি এখানে সরাসরি আপলোড করুন:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

    [cite: 1]elif call.data == "all_services":
       [cite: 1]conn.close()
       [cite: 1]markup = get_categories_markup()
       [cite: 1]bot.edit_message_text(f"{pe('welcome_shop')} <b>আমাদের কাছে নিচের সার্ভিসগুলো রয়েছে:</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data == "group_mail":
       [cite: 1]cursor.execute("SELECT cat_id, name, price, has_emoji FROM categories WHERE group_type = 'mail'")
       [cite: 1]mail_cats = cursor.fetchall()
        [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for cat_id, name, price, has_em in mail_cats:
           [cite: 1]sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
           [cite: 1]sub_cur = sub_conn.cursor()
           [cite: 1]sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
           [cite: 1]stock_count = sub_cur.fetchone()[0]
           [cite: 1]sub_conn.close()
           [cite: 1]markup.add(premium_inline_button(f"✉️ {name} - ৳{price} (Stock: {stock_count})", "mail_item", callback_data=f"buy_{cat_id}"))
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="all_services"))

       [cite: 1]bot.edit_message_text(f"{pe('mail_cat')} <b>All Mail Services</b> {pe('mail_cat')}\n\nনিচের মেইলগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data == "group_proxy":
       [cite: 1]cursor.execute("SELECT cat_id, name, price, has_emoji FROM categories WHERE group_type = 'proxy'")
       [cite: 1]proxy_cats = cursor.fetchall()
        [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for cat_id, name, price, has_em in proxy_cats:
           [cite: 1]sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
           [cite: 1]sub_cur = sub_conn.cursor()
           [cite: 1]sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
           [cite: 1]stock_count = sub_cur.fetchone()[0]
           [cite: 1]sub_conn.close()
           [cite: 1]markup.add(premium_inline_button(f"🌐 {name} - ৳{price} (Stock: {stock_count})", "proxy_item", callback_data=f"buy_{cat_id}"))
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="all_services"))

       [cite: 1]bot.edit_message_text(f"{pe('proxy_cat')} <b>All Proxy Services</b> {pe('proxy_cat')}\n\nনিচের প্রক্সিগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data == "special_cat_vpn_service":
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("⏳ 3 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_3d"),
           [cite: 1]premium_inline_button("⏳ 7 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_7d"),
           [cite: 1]premium_inline_button("⏳ 9 Day", "vpn_service_cat", callback_data="vpn_dur_vpn_9d"),
           [cite: 1]premium_inline_button("⏳ 1 Month", "vpn_service_cat", callback_data="vpn_dur_vpn_1m"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="all_services")
        )
       [cite: 1]bot.edit_message_text(f"{pe('vpn_service_cat')} <b>VPN Service</b> {pe('vpn_service_cat')}\n\nআপনি কতদিনের জন্য VPN নিতে চাচ্ছেন মেয়াদের ক্যাটাগরি সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("vpn_dur_"):
       [cite: 1]dur_cat = call.data.replace("vpn_dur_", "")
       [cite: 1]cursor.execute("SELECT sub_id, sub_name, price, has_emoji FROM sub_services WHERE cat_id = ?", (dur_cat,))
        [cite: 1]sub_items = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]dur_text_map = {
            "vpn_3d": "৩ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_7d": "৭ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_9d": "৯ দিন মেয়াদের VPN গুলো নিচে দেওয়া হলো:",
            "vpn_1m": "১ মাস মেয়াদের VPN গুলো নিচে দেওয়া হলো:"
        }
       [cite: 1]dynamic_heading = dur_text_map.get(dur_cat, "নিচের VPN গুলো থেকে আপনার পছন্দের সার্ভিসটি সিলেক্ট করুন:")

       [cite: 1]if not sub_items:
           [cite: 1]bot.answer_callback_query(call.id, "এই মেয়াদের ভিপিএন বর্তমানে স্টকে নেই!", show_alert=True)
           [cite: 1]return

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for sub_id, sub_name, price, has_em in sub_items:
           [cite: 1]markup.add(premium_inline_button(f"🛡️ {sub_name} - ৳{price}", "vpn_service_cat", callback_data=f"subbuy_{sub_id}"))
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="special_cat_vpn_service"))

       [cite: 1]bot.edit_message_text(f"{pe('vpn_service_cat')} <b>VPN Packages</b>\n\n{dynamic_heading}", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data == "special_cat_telegram_premium":
       [cite: 1]cursor.execute("SELECT sub_id, sub_name, price, has_emoji FROM sub_services WHERE cat_id = 'telegram_premium'")
       [cite: 1]sub_items = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for sub_id, sub_name, price, has_em in sub_items:
           [cite: 1]markup.add(premium_inline_button(f"💎 {sub_name} - ৳{price}", "telegram_premium_cat", callback_data=f"subbuy_{sub_id}"))
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="all_services"))

       [cite: 1]bot.edit_message_text(f"{pe('telegram_premium_cat')} <b>Telegram Premium Buy</b> {pe('telegram_premium_cat')}\n\nনিচের প্যাকেজগুলো থেকে আপনার পছন্দমতো সিলেক্ট করুন:", call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("subbuy_"):
       [cite: 1]sub_id = call.data.split("_")[1]
       [cite: 1]cursor.execute("SELECT cat_id, sub_name, price FROM sub_services WHERE sub_id = ?", (sub_id,))
       [cite: 1]sub_data = cursor.fetchone()
       [cite: 1]conn.close()

       [cite: 1]if not sub_data:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} দুঃখিত, এই প্যাকেজটি পাওয়া যায়নি।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]cat_id, sub_name, price = sub_data
       [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
       [cite: 1]cursor = conn.cursor()
       [cite: 1]cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
       [cite: 1]bal_res = cursor.fetchone()
       [cite: 1]user_bal = bal_res[0] if bal_res else 0.0
       [cite: 1]conn.close()

       [cite: 1]if user_bal < price:
            [cite: 1]bot.send_message(call.message.chat.id, f"{pe('insufficient_bal')} পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন ৳{price}, আপনার আছে ৳{user_bal}।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]user_temp_deposit[user_id] = {"step": "waiting_service_username", "cat_id": cat_id, "sub_name": sub_name, "price": price}
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass

       [cite: 1]bot.send_message(call.message.chat.id, f"✨ আপনি সিলেক্ট করেছেন: <b>{sub_name}</b> (মূল্য: ৳{price}) ✨\n\n{pe('list_point')} এখন যে আইডিতে সার্ভিস নিতে চাচ্ছেন, সেটির সঠিক <b>Telegram Username</b> বা প্রোফাইল আইডি চ্যাটে লিখে পাঠান:", parse_mode="HTML")
       [cite: 1]return

   [cite: 1]elif call.data.startswith("buy_"):
       [cite: 1]cat_id = call.data.replace("buy_", "")
       [cite: 1]cursor.execute("SELECT name, price, group_type FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cat = cursor.fetchone()
       [cite: 1]cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
       [cite: 1]stock_count_res = cursor.fetchone()
       [cite: 1]stock_count = stock_count_res[0] if stock_count_res else 0
       [cite: 1]conn.close()

       [cite: 1]if stock_count == 0 or not cat:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('no_stock')} দুঃখিত! এই মুহূর্তে এই আইটেমের স্টক শেষ।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]back_target = f"group_{cat[2]}" if cat[2] in ('mail', 'proxy') else "all_services"

       [cite: 1]user_temp_deposit[user_id] = {"step": "waiting_custom_qty", "cat_id": cat_id}
       [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("📦 1 Pcs", "qty_select", callback_data=f"qty_{cat_id}_1"),
           [cite: 1]premium_inline_button("📦 5 Pcs", "qty_select", callback_data=f"qty_{cat_id}_5"),
           [cite: 1]premium_inline_button("📦 10 Pcs", "qty_select", callback_data=f"qty_{cat_id}_10"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data=back_target)
        )
       [cite: 1]msg_text = f"{pe('box_package')} <b>{cat[0]}</b>\n{pe('money_spent')} Price: ৳{cat[1]}\nStock: {stock_count} Pcs\n\nSelect quantity:\n{pe('list_point')} অধিক নিতে চাইলে নিচে চ্যাটে কাঙ্ক্ষিত পিস সংখ্যা লিখে পাঠান।"
       [cite: 1]try: bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
       [cite: 1]except Exception: bot.send_message(call.message.chat.id, msg_text, parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("qty_"):
       [cite: 1]parts = call.data.split("_")
       [cite: 1]qty_str, cat_id = parts[-1], "_".join(parts[1:-1])
       [cite: 1]conn.close()
       [cite: 1]if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_custom_qty":
           [cite: 1]del user_temp_deposit[user_id]
       [cite: 1]process_purchase(call.message.chat.id, user_id, cat_id, int(qty_str))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]return

   [cite: 1]elif call.data.startswith("btn_emojichoice_") and user_id == ADMIN_ID:
       [cite: 1]choice = call.data.split("_")[2]
       [cite: 1]has_em = 1 if choice == "yes" else 0

       [cite: 1]if user_id in admin_states and "pending_btn_data" in admin_states[user_id]:
            [cite: 1]pdata = admin_states[user_id]["pending_btn_data"]
           [cite: 1]mode = pdata["mode"]

           [cite: 1]if mode == "new_cat":
               [cite: 1]c_name, c_price = pdata["name"], pdata["price"]
               [cite: 1]clean_id_base = "".join([c for c in c_name.lower() if c.isalnum() or c == '_'])[:12]
               [cite: 1]new_cat_id = f"{clean_id_base}_{str(uuid.uuid4())[:6]}"
               [cite: 1]g_type = 'proxy' if 'proxy' in c_name.lower() else 'mail'
               [cite: 1]cursor.execute("INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?, ?)", (new_cat_id, c_name, c_price, has_em, g_type))
               [cite: 1]conn.commit()
               [cite: 1]bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে নতুন বাটন যুক্ত হয়েছে!\nনাম: <code>{c_name}</code>\nমূল্য: ৳{c_price}\nগ্রুপ: {'Proxy' if g_type=='proxy' else 'Mail'}", parse_mode="HTML")

           [cite: 1]elif mode == "edit_cat":
               [cite: 1]c_id, c_name, c_price = pdata["cat_id"], pdata["name"], pdata["price"]
               [cite: 1]cursor.execute("UPDATE categories SET name = ?, price = ?, has_emoji = ? WHERE cat_id = ?", (c_name, c_price, has_em, c_id))
               [cite: 1]conn.commit()
               [cite: 1]bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে ক্যাটাগরি আপডেট হয়েছে!\nনাম: <code>{c_name}</code>\nমূল্য: ৳{c_price}", parse_mode="HTML")

           [cite: 1]elif mode == "new_sub":
               [cite: 1]c_id, s_name, s_price = pdata["cat_id"], pdata["name"], pdata["price"]
               [cite: 1]cursor.execute("INSERT INTO sub_services (cat_id, sub_name, price, has_emoji) VALUES (?, ?, ?, ?)", (c_id, s_name, s_price, has_em))
               [cite: 1]conn.commit()
               [cite: 1]bot.send_message(call.message.chat.id, f"{pe('step_tick')} সফলভাবে নতুন সাব-বাটন যুক্ত হয়েছে!\nনাম: <code>{s_name}</code>\nমূল্য: ৳{s_price}", parse_mode="HTML")

           [cite: 1]del admin_states[user_id]
       [cite: 1]conn.close()
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]return

    # ----------------- Stock Management (Admin Panel) -----------------
   [cite: 1]elif call.data == "admin_add_stock_menu" and user_id == ADMIN_ID:
       [cite: 1]if user_id in admin_states: del admin_states[user_id]
       [cite: 1]cursor.execute("SELECT cat_id, name FROM categories")
       [cite: 1]categories = cursor.fetchall()
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for cat_id, name in categories:
           [cite: 1]sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
           [cite: 1]sub_cur = sub_conn.cursor()
           [cite: 1]sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
           [cite: 1]s_count = sub_cur.fetchone()[0]
           [cite: 1]sub_conn.close()
           [cite: 1]markup.add(premium_inline_button(f"📦 {name} (Stock: {s_count} Pcs)", "manage_stock", callback_data=f"manage_stock_{cat_id}"))
        
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
        [cite: 1]bot.send_message(call.message.chat.id, f"{pe('box_package')} <b>Stock Management:</b>\nযে সার্ভিসের স্টক ম্যানেজ করতে চান তা সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

    [cite: 1]elif call.data.startswith("manage_stock_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("manage_stock_", "")
       [cite: 1]cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cat_res = cursor.fetchone()
       [cite: 1]cat_name = cat_res[0] if cat_res else cat_id

       [cite: 1]cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
       [cite: 1]stock_count = cursor.fetchone()[0]
       [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("📥 Add New Stock File (.txt)", "add_balance", callback_data=f"select_stock_{cat_id}"),
           [cite: 1]premium_inline_button("📤 Download Current Stock (.txt)", "download_txt", callback_data=f"download_stock_{cat_id}"),
           [cite: 1]premium_inline_button(f"🗑️ Remove All Stock ({stock_count} Pcs)", "delete_trash", callback_data=f"clear_stock_{cat_id}"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_add_stock_menu")
        )
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
        [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('box_package')} <b>Stock Management:</b> {cat_name}\nবর্তমান স্টক সংখ্যা: <b>{stock_count} পিস</b>", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("download_stock_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("download_stock_", "")
       [cite: 1]cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cat_name = cursor.fetchone()[0]
       [cite: 1]cursor.execute("SELECT content FROM stock WHERE cat_id = ? ORDER BY id ASC", (cat_id,))
       [cite: 1]rows = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]if not rows:
           [cite: 1]bot.answer_callback_query(call.id, "এই মুহূর্তে এই ক্যাটাগরিতে কোনো স্টক নেই!", show_alert=True)
           [cite: 1]return

       [cite: 1]file_content = "\n".join([r[0] for r in rows])
       [cite: 1]file_path = f"stock_{cat_id}.txt"
       [cite: 1]with open(file_path, "w", encoding="utf-8") as f:
           [cite: 1]f.write(file_content)

       [cite: 1]with open(file_path, "rb") as f:
           [cite: 1]bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} <b>{cat_name}</b> এর বর্তমান সমস্ত স্টক ফাইল:", parse_mode="HTML")
       [cite: 1]os.remove(file_path)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("clear_stock_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("clear_stock_", "")
       [cite: 1]cursor.execute("DELETE FROM stock WHERE cat_id = ?", (cat_id,))
       [cite: 1]conn.commit()
        [cite: 1]conn.close()
       [cite: 1]bot.answer_callback_query(call.id, "স্টক সফলভাবে মুছে ফেলা হয়েছে!", show_alert=True)

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
       [cite: 1]sub_cur = sub_conn.cursor()
       [cite: 1]sub_cur.execute("SELECT cat_id, name FROM categories")
       [cite: 1]categories = sub_cur.fetchall()
       [cite: 1]for cid, name in categories:
           [cite: 1]sub_cur.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cid,))
           [cite: 1]s_count = sub_cur.fetchone()[0]
           [cite: 1]markup.add(premium_inline_button(f"📦 {name} (Stock: {s_count} Pcs)", "manage_stock", callback_data=f"manage_stock_{cid}"))
       [cite: 1]sub_conn.close()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))

       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('box_package')} স্টক মুছে ফেলা হয়েছে। অন্য সার্ভিস সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("select_stock_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("select_stock_", "")
       [cite: 1]admin_states[user_id] = {"action": "waiting_stock_file", "cat_id": cat_id}
       [cite: 1]cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
        [cite: 1]cat_name = cursor.fetchone()[0]
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data=f"manage_stock_{cat_id}"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('box_package')} আপনি সিলেক্ট করেছেন: <b>{cat_name}</b>\n\nএখন নতুন স্টক ফাইল (.txt) সরাসরি এই চ্যাটে ফাইল হিসেবে আপলোড করে পাঠান:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

    # ----------------- Other Admin Panel Callbacks -----------------
   [cite: 1]elif call.data == "admin_analytics" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT COUNT(*) FROM users")
        [cite: 1]total_users = cursor.fetchone()[0]
       [cite: 1]cursor.execute("SELECT SUM(balance) FROM users")
       [cite: 1]res_sum = cursor.fetchone()
       [cite: 1]total_user_balance = res_sum[0] if res_sum and res_sum[0] is not None else 0.0
       [cite: 1]cursor.execute("SELECT user_id, first_name, balance FROM users ORDER BY user_id DESC")
       [cite: 1]all_registered = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]analytics_text = (
           [cite: 1]f"{pe('stats_chart')} <b>Live Bot Analytics & Statistics</b>\n\n"
           [cite: 1]f"{pe('profile_user')} মোট জয়েনকৃত ইউজার: <b>{total_users} জন</b>\n"
           [cite: 1]f"{pe('balance_coin')} ইউজারদের মোট একাউন্ট ব্যালেন্স: <b>৳{total_user_balance}</b>\n\n"
           [cite: 1]f"{pe('list_point')} <b>সাম্প্রতিক ইউজার তালিকা:</b>\n"
        )
       [cite: 1]for u_id, u_name, u_bal in all_registered[:15]:
           [cite: 1]safe_name = u_name or "User"
           [cite: 1]analytics_text += f"• {safe_name} (<code>{u_id}</code>) - ৳{u_bal}\n"

       [cite: 1]markup = InlineKeyboardMarkup()
        [cite: 1]markup.add(
           [cite: 1]premium_inline_button("📥 Download Bot Analysis TXT File", "download_txt", callback_data="admin_download_analytics_txt"),
           [cite: 1]premium_inline_button("🔄 Refresh Live Data", "refresh_data", callback_data="admin_analytics"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_main")
        )
       [cite: 1]try: bot.edit_message_text(analytics_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
       [cite: 1]except Exception: pass

   [cite: 1]elif call.data == "admin_download_analytics_txt" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT user_id, first_name FROM users ORDER BY user_id DESC")
       [cite: 1]all_users = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]if not all_users:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} বোর্ডে কোনো ইউজرهای ডাটা পাওয়া যায়নি!", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]file_content = ""
       [cite: 1]for u_id, u_name in all_users:
           [cite: 1]safe_name = u_name or "User"
           [cite: 1]file_content += f"{u_id} | {safe_name}\n"

        [cite: 1]file_path = "bot_analytics_users.txt"
       [cite: 1]with open(file_path, "w", encoding="utf-8") as f:
            [cite: 1]f.write(file_content)

       [cite: 1]with open(file_path, "rb") as f:
           [cite: 1]bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} Bot Analytics & User List (.txt)\nসকল ইউজারের আইডি দিয়ে তৈরি করা ফাইল:")
       [cite: 1]os.remove(file_path)

   [cite: 1]elif call.data == "admin_member_balance_list" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT user_id, first_name, balance FROM users WHERE balance > 0 ORDER BY balance DESC")
       [cite: 1]users_with_money = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]list_text = f"{pe('balance_coin')} <b>যেসব মেম্বারদের অ্যাকাউন্টে টাকা আছে তাদের তালিকা:</b>\n\n"
       [cite: 1]if not users_with_money:
           [cite: 1]list_text += f"{pe('warn_icon')} এই মুহূর্তে কারও অ্যাকাউন্টে ব্যালেন্স নেই."
       [cite: 1]else:
           [cite: 1]for idx, (u_id, u_name, u_bal) in enumerate(users_with_money[:20], 1):
               [cite: 1]safe_name = u_name or "User"
               [cite: 1]list_text += f"{idx}. {safe_name} | ID: <code>{u_id}</code> | ব্যালেন্স: <b>৳{u_bal}</b>\n"

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("📥 Download Balance List TXT", "download_txt", callback_data="admin_download_balance_txt"),
           [cite: 1]premium_inline_button("🔄 Recover Balance List (.txt)", "recover_balance", callback_data="admin_recover_balance_list"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_main")
        )
       [cite: 1]try: bot.edit_message_text(list_text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
       [cite: 1]except Exception: pass

   [cite: 1]elif call.data == "admin_download_balance_txt" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT user_id, balance, first_name FROM users WHERE balance > 0 ORDER BY balance DESC")
       [cite: 1]users_with_money = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]if not users_with_money:
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই মুহূর্তে কারও অ্যাকাউন্টে ব্যালেন্স নেই!", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]file_content = ""
       [cite: 1]for u_id, u_bal, u_name in users_with_money:
           [cite: 1]file_content += f"{u_id} | {u_bal}\n"

       [cite: 1]file_path = "all_member_balance_list.txt"
       [cite: 1]with open(file_path, "w", encoding="utf-8") as f:
           [cite: 1]f.write(file_content)

       [cite: 1]with open(file_path, "rb") as f:
           [cite: 1]bot.send_document(call.message.chat.id, f, caption=f"{pe('box_package')} All Member Balance List (.txt)\nব্যালেন্সধারী মেম্বারদের তালিকা ডাউনলোড হয়েছে:")
       [cite: 1]os.remove(file_path)

   [cite: 1]elif call.data == "admin_recover_balance_list" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_recover_balance_txt"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('recover_balance')} <b>Recover Balance List (.txt)</b>\n\nপূর্বে ডাউনলোড করা <code>all_member_balance_list.txt</code> ফাইলটি এখানে আপলোড করুন.", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data == "admin_all_post_edit" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("1️⃣ Edit Welcome Post", "post_edit", callback_data="edit_post_welcome_msg"),
           [cite: 1]premium_inline_button("2️⃣ Edit Channel Not Joined Warning", "post_edit", callback_data="edit_post_not_joined_msg"),
           [cite: 1]premium_inline_button("3️⃣ Edit Support Text", "post_edit", callback_data="edit_post_support_msg"),
           [cite: 1]premium_inline_button("4️⃣ Edit Deposit Information Text", "post_edit", callback_data="edit_post_deposit_info_msg"),
           [cite: 1]premium_inline_button("🔙 Back to Admin", "back_button", callback_data="admin_main")
        )
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('post_edit')} <b>All Post Edit</b>\n\nযেই পোস্টটি এডিট করতে চান সেটির ওপর ক্লিক করুন:", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("edit_post_") and user_id == ADMIN_ID:
       [cite: 1]post_key = call.data.replace("edit_post_", "")
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_generic_post_update", "post_key": post_key}
       [cite: 1]current_text = get_setting_msg(post_key, "খালি")
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_all_post_edit"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('post_edit')} <b>Editing Post:</b> <code>{post_key}</code>\n\n<b>বর্তমান লেখা:</b>\n------------------\n{current_text}\n------------------\n\nনতুন লেখাটি পাঠান:", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data == "admin_all_button_edit" and user_id == ADMIN_ID:
       [cite: 1]cursor.execute("SELECT cat_id, name FROM categories")
       [cite: 1]categories = cursor.fetchall()
       [cite: 1]cursor.execute("SELECT sub_id, sub_name FROM sub_services")
       [cite: 1]sub_services = cursor.fetchall()
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]markup.add(InlineKeyboardButton("--- Main Categories ---", callback_data="ignore"))
       [cite: 1]for cid, name in categories:
           [cite: 1]markup.add(premium_inline_button(name, "edit_pencil", callback_data=f"editbtn_cat_{cid}"))
       [cite: 1]if sub_services:
           [cite: 1]markup.add(InlineKeyboardButton("--- Sub Packages / VPNs ---", callback_data="ignore"))
           [cite: 1]for sid, sname in sub_services:
               [cite: 1]markup.add(premium_inline_button(sname, "edit_pencil", callback_data=f"editbtn_sub_{sid}"))
       [cite: 1]markup.add(premium_inline_button("🔙 Back to Admin", "back_button", callback_data="admin_main"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('button_edit')} <b>All Button Edit</b>\n\nযেই বাটনটি এডিট করতে চান সিলেক্ট করুন:", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("editbtn_") and user_id == ADMIN_ID:
       [cite: 1]parts = call.data.split("_")
        [cite: 1]btn_type, btn_id = parts[1], "_".join(parts[2:])
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_generic_btn_update", "btn_type": btn_type, "btn_id": btn_id}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_all_button_edit"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('edit_pencil')} এই বাটনটির জন্য নতুন <b>নাম (Text)</b> লিখে পাঠান:", parse_mode="HTML", reply_markup=markup)

    [cite: 1]elif call.data == "admin_edit_services" and user_id == ADMIN_ID:
       [cite: 1]if user_id in admin_states: del admin_states[user_id]
       [cite: 1]cursor.execute("SELECT cat_id, name, price FROM categories")
       [cite: 1]categories = cursor.fetchall()
       [cite: 1]conn.close()
       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
        
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("✉️ Manage Sub-Buttons: All Mail Service", "edit_service", callback_data="editsubs_group_mail"),
           [cite: 1]premium_inline_button("🌐 Manage Sub-Buttons: All Proxy Service", "edit_service", callback_data="editsubs_group_proxy")
        )
        
       [cite: 1]special_ids = ["telegram_premium", "vpn_service"]
       [cite: 1]regular_cats = [c for c in categories if c[0] not in special_ids and c[0] not in ['hotmail', 'outlook', 'Outlook fr', 'Ig Hotmail', 'proxy']]
       [cite: 1]special_cats = [c for c in categories if c[0] in special_ids]
        
       [cite: 1]for cat_id, name, price in regular_cats:
           [cite: 1]sub_conn = sqlite3.connect("shop_bot.db", timeout=30)
           [cite: 1]sub_cursor = sub_conn.cursor()
           [cite: 1]sub_cursor.execute("SELECT COUNT(*) FROM stock WHERE cat_id = ?", (cat_id,))
           [cite: 1]stock_count = sub_cursor.fetchone()[0]
           [cite: 1]sub_conn.close()
           [cite: 1]markup.add(
               [cite: 1]premium_inline_button(f"⚙️ {name} | ৳{price} | Stock: {stock_count}", "edit_service", callback_data=f"editcat_{cat_id}"),
               [cite: 1]premium_inline_button(f"🗑️ Delete {name}", "delete_trash", callback_data=f"confirm_del_{cat_id}")
            )
            
       [cite: 1]for cat_id, name, price in special_cats:
           [cite: 1]markup.add(
               [cite: 1]premium_inline_button(f"⚙️ Manage Sub-Buttons: {name}", "edit_service", callback_data=f"editsubs_{cat_id}"),
               [cite: 1]premium_inline_button(f"🗑️ Delete {name}", "delete_trash", callback_data=f"confirm_del_{cat_id}")
            )
        
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("➕ Add New Button / Service", "add_balance", callback_data="admin_add_new_btn"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_main")
        )
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('edit_service')} সার্ভিস এডিট বা ডিলিট করতে নিচের বাটনগুলোতে ক্লিক করুন:", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("confirm_del_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("confirm_del_", "")
       [cite: 1]cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cat_res = cursor.fetchone()
       [cite: 1]cat_name = cat_res[0] if cat_res else "এই সার্ভিসটি"
       [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
       [cite: 1]markup.add(
           [cite: 1]premium_inline_button("✅ Yes (Delete)", "approve_btn", callback_data=f"delcat_{cat_id}"),
           [cite: 1]premium_inline_button("❌ No (Cancel)", "reject_btn", callback_data="admin_edit_services")
        )
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} <b>সতর্কবার্তা!</b>\n\nআপনি কি সত্যি <b>{cat_name}</b> বাটনটি ডিলিট করতে চাচ্ছেন?", parse_mode="HTML", reply_markup=markup)
       [cite: 1]return

   [cite: 1]elif call.data.startswith("editsubs_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("editsubs_", "")
        [cite: 1]if cat_id == "vpn_service":
           [cite: 1]conn.close()
           [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
           [cite: 1]markup.add(
               [cite: 1]premium_inline_button("⏳ Manage 3 Day", "edit_service", callback_data="editsubs_vpn_3d"),
               [cite: 1]premium_inline_button("⏳ Manage 7 Day", "edit_service", callback_data="editsubs_vpn_7d"),
               [cite: 1]premium_inline_button("⏳ Manage 9 Day", "edit_service", callback_data="editsubs_vpn_9d"),
               [cite: 1]premium_inline_button("⏳ Manage 1 Month", "edit_service", callback_data="editsubs_vpn_1m"),
               [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_edit_services")
            )
           [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
           [cite: 1]except Exception: pass
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>VPN Service Sub-Packages Manage:</b>\nমেয়াদ অনুযায়ী প্যাকেজ ম্যানেজ করুন:", parse_mode="HTML", reply_markup=markup)
           [cite: 1]return

       [cite: 1]if cat_id in ("group_mail", "group_proxy"):
           [cite: 1]g_type = 'mail' if cat_id == "group_mail" else 'proxy'
            [cite: 1]cursor.execute("SELECT cat_id, name, price FROM categories WHERE group_type = ?", (g_type,))
           [cite: 1]items = cursor.fetchall()
           [cite: 1]conn.close()

           [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
           [cite: 1]for c_id, c_name, c_price in items:
               [cite: 1]markup.add(
                   [cite: 1]premium_inline_button(f"⚙️ Edit: {c_name} (৳{c_price})", "edit_service", callback_data=f"editcat_{c_id}"),
                   [cite: 1]premium_inline_button(f"🗑️ Delete: {c_name}", "delete_trash", callback_data=f"confirm_del_{c_id}")
                )
            
           [cite: 1]markup.add(
               [cite: 1]premium_inline_button("➕ Add New Service / Button", "add_balance", callback_data="admin_add_new_btn"),
               [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_edit_services")
            )
           [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
           [cite: 1]except Exception: pass
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>Manage {('Mail Services' if g_type=='mail' else 'Proxy Services')}:</b>", parse_mode="HTML", reply_markup=markup)
           [cite: 1]return

       [cite: 1]cursor.execute("SELECT sub_id, sub_name, price FROM sub_services WHERE cat_id = ?", (cat_id,))
       [cite: 1]subs = cursor.fetchall()
       [cite: 1]conn.close()

       [cite: 1]markup = InlineKeyboardMarkup(row_width=1)
       [cite: 1]for sub_id, sub_name, price in subs:
           [cite: 1]markup.add(premium_inline_button(f"🗑️ Delete: {sub_name} (৳{price})", "delete_trash", callback_data=f"delsub_{sub_id}_{cat_id}"))
        
        [cite: 1]markup.add(
           [cite: 1]premium_inline_button("➕ Add New Package", "add_balance", callback_data=f"addsub_{cat_id}"),
           [cite: 1]premium_inline_button("🔙 Back", "back_button", callback_data="admin_edit_services")
        )
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('edit_service')} <b>Manage Sub-Buttons:</b>", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("delsub_") and user_id == ADMIN_ID:
       [cite: 1]parts = call.data.split("_")
       [cite: 1]sub_id, cat_id = parts[1], parts[2]
        [cite: 1]cursor.execute("DELETE FROM sub_services WHERE sub_id = ?", (sub_id,))
       [cite: 1]conn.commit()
       [cite: 1]conn.close()
       [cite: 1]bot.answer_callback_query(call.id, "প্যাকেজ ডিলিট হয়েছে!")
       [cite: 1]return

   [cite: 1]elif call.data.startswith("addsub_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("addsub_", "")
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "adding_sub_item", "cat_id": cat_id}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data=f"editsubs_{cat_id}"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('add_balance')} নতুন প্যাকেজের নাম এবং দাম লিখে পাঠান:\n<code>[Package Name] [Price]</code>", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("editcat_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("editcat_", "")
       [cite: 1]cursor.execute("SELECT name, price FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cat = cursor.fetchone()
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "editing_cat", "cat_id": cat_id}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_edit_services"))
       [cite: 1]edit_prompt = f"{pe('edit_pencil')} এডিট করছেন: <b>{cat[0]}</b> (বর্তমান মূল্য: ৳{cat[1]})\n\nনতুন নাম এবং রেট লিখে পাঠান。\n<b>ফরম্যাট:</b> <code>[নতুন নাম] [রেট]</code>"
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
        [cite: 1]except Exception: pass
       [cite: 1]bot.send_message(call.message.chat.id, edit_prompt, parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("delcat_") and user_id == ADMIN_ID:
       [cite: 1]cat_id = call.data.replace("delcat_", "")
       [cite: 1]cursor.execute("DELETE FROM categories WHERE cat_id = ?", (cat_id,))
       [cite: 1]cursor.execute("DELETE FROM stock WHERE cat_id = ?", (cat_id,))
       [cite: 1]cursor.execute("DELETE FROM sub_services WHERE cat_id = ?", (cat_id,))
       [cite: 1]conn.commit()
        [cite: 1]conn.close()
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('step_tick')} সার্ভিসটি সফলভাবে ডিলিট করা হয়েছে!", parse_mode="HTML")

   [cite: 1]elif call.data == "admin_add_new_btn" and user_id == ADMIN_ID:
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "adding_new_cat"}
       [cite: 1]markup = InlineKeyboardMarkup()
       [cite: 1]markup.add(premium_inline_button("🔙 Back", "back_button", callback_data="admin_edit_services"))
       [cite: 1]try: bot.delete_message(call.message.chat.id, call.message.message_id)
       [cite: 1]except Exception: pass
        [cite: 1]bot.send_message(call.message.chat.id, f"{pe('add_balance')} নতুন বাটন যোগ করতে ফরম্যাটে নাম এবং দাম লিখে পাঠান:\n<code>[Button Name] [Price]</code>", parse_mode="HTML", reply_markup=markup)

   [cite: 1]elif call.data.startswith("app_") and user_id == ADMIN_ID:
       [cite: 1]req_id = call.data.split("_")[1]
       [cite: 1]if req_id in pending_deposits:
           [cite: 1]data = pending_deposits[req_id]
           [cite: 1]target_user, amount, method = data["user_id"], data["amount"], data.get("method", "Payment")
           [cite: 1]cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_user,))
           [cite: 1]if not cursor.fetchone():
               [cite: 1]cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_user, "User", amount))
            [cite: 1]else:
               [cite: 1]cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_user))
           [cite: 1]conn.commit()
           [cite: 1]conn.close()
           [cite: 1]bot.send_message(target_user, f"{pe('deposit_success')} <b>আপনার ডিপোজিট সফল হয়েছে!</b>\nআপনার একাউন্টে <b>৳{amount}</b> যোগ করা হয়েছে। এখন আপনি কেনাকাটা করতে পারেন।", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
           [cite: 1]try:
               [cite: 1]bot.edit_message_caption(f"Approved Successfully (User ID: {target_user}, Amount: ৳{amount}, Method: {method})", call.message.chat.id, call.message.message_id)
           [cite: 1]except Exception:
               [cite: 1]bot.send_message(call.message.chat.id, f"✅ Approved Successfully (User ID: {target_user}, Amount: ৳{amount})")
           [cite: 1]del pending_deposits[req_id]
       [cite: 1]else:
           [cite: 1]conn.close()
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে!", parse_mode="HTML")

   [cite: 1]elif call.data.startswith("rej_") and user_id == ADMIN_ID:
       [cite: 1]req_id = call.data.split("_")[1]
       [cite: 1]if req_id in pending_deposits:
           [cite: 1]data = pending_deposits[req_id]
           [cite: 1]target_user = data["user_id"]
           [cite: 1]conn.close()
           [cite: 1]bot.send_message(target_user, f"{pe('warn_icon')} আপনি ভুল তথ্য বা স্ক্রিনশট দিয়েছেন, তাই আপনার অর্ডারটি রিজেক্ট করা হলো। সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন।", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
           [cite: 1]try:
               [cite: 1]bot.edit_message_caption(f"Rejected (User ID: {target_user})", call.message.chat.id, call.message.message_id)
           [cite: 1]except Exception:
               [cite: 1]bot.send_message(call.message.chat.id, f"❌ Rejected (User ID: {target_user})")
           [cite: 1]del pending_deposits[req_id]
       [cite: 1]else:
           [cite: 1]conn.close()
           [cite: 1]bot.send_message(call.message.chat.id, f"{pe('warn_icon')} এই রিকোয়েস্টটি ইতিমধ্যে প্রসেস করা হয়েছে!", parse_mode="HTML")

   [cite: 1]elif call.data.startswith("complete_order_") and user_id == ADMIN_ID:
       [cite: 1]target_user = int(call.data.split("_")[2])
       [cite: 1]conn.close()
       [cite: 1]admin_states[user_id] = {"action": "waiting_delivery_content", "target_user": target_user}
       [cite: 1]bot.send_message(call.message.chat.id, f"{pe('list_point')} ইউজার ID: <code>{target_user}</code> এর অর্ডারের জন্য মেসেজ বা ডাটা লিখে পাঠান:", parse_mode="HTML")

   [cite: 1]else:
       [cite: 1]conn.close()

# ----------------- Document/File Handler -----------------
[cite: 1]@bot.message_handler(content_types=['document'])
[cite: 1]def handle_stock_file(message):
   [cite: 1]update_owner_premium_status(message.from_user)
   [cite: 1]user_id = message.from_user.id
   [cite: 1]save_user_id_to_file(user_id)
    
   [cite: 1]if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
       [cite: 1]file_id = message.document.file_id
       [cite: 1]process_deposit_submission(message, file_id, is_document=True)
       [cite: 1]return

   [cite: 1]if user_id == ADMIN_ID and user_id in admin_states:
       [cite: 1]action = admin_states[user_id].get("action")
        
       [cite: 1]if action == "waiting_stock_file":
           [cite: 1]cat_id = admin_states[user_id]["cat_id"]
           [cite: 1]try:
               [cite: 1]file_info = bot.get_file(message.document.file_id)
               [cite: 1]downloaded_file = bot.download_file(file_info.file_path)
               [cite: 1]file_content = downloaded_file.decode('utf-8', errors='ignore')
               [cite: 1]lines = [line.strip() for line in file_content.splitlines() if line.strip()]
                
               [cite: 1]if not lines:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} ফাইলটি খালি রয়েছে।", parse_mode="HTML")
                   [cite: 1]return
                
               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
               [cite: 1]cursor = conn.cursor()
               [cite: 1]added_count = 0
               [cite: 1]for line in lines:
                   [cite: 1]cursor.execute("INSERT INTO stock (cat_id, content) VALUES (?, ?)", (cat_id, line))
                   [cite: 1]added_count += 1
               [cite: 1]conn.commit()
                
               [cite: 1]cursor.execute("SELECT user_id FROM users")
               [cite: 1]all_users = cursor.fetchall()
               [cite: 1]cursor.execute("SELECT name FROM categories WHERE cat_id = ?", (cat_id,))
                [cite: 1]cat_name = cursor.fetchone()[0]
               [cite: 1]conn.close()
                
               [cite: 1]broadcast_text = (
                   [cite: 1]f"{pe('alarm_bell')} <b>নতুন স্টক আপডেট!</b>\n\n"
                   [cite: 1]f"আমাদের বটে নতুন স্টক যুক্ত হয়েছে: <b>{cat_name}</b>\n"
                    [cite: 1]f"এখনই আপনার অ্যাকাউন্ট থেকে পর্যাপ্ত ব্যালেন্স দিয়ে খুব সহজে কিনে নিন। স্টক সীমিত!"
                )
               [cite: 1]for u in all_users:
                   [cite: 1]try: bot.send_message(u[0], broadcast_text, parse_mode="HTML", reply_markup=get_permanent_keyboard(u[0]))
                   [cite: 1]except Exception: pass

               [cite: 1]del admin_states[user_id]
               [cite: 1]bot.reply_to(message, f"{pe('step_tick')} সফলভাবে মোট <b>{added_count}টি</b> স্টক যোগ করা হয়েছে এবং মেম্বারদের নোটিফিকেশন পাঠানো হয়েছে!", parse_mode="HTML")
           [cite: 1]except Exception as e:
               [cite: 1]bot.reply_to(message, f"ফাইল প্রসেস করতে সমস্যা হয়েছে: {e}")
           [cite: 1]return

       [cite: 1]elif action == "waiting_recover_balance_txt":
           [cite: 1]try:
               [cite: 1]file_info = bot.get_file(message.document.file_id)
               [cite: 1]downloaded_file = bot.download_file(file_info.file_path)
               [cite: 1]file_content = downloaded_file.decode('utf-8', errors='ignore')
               [cite: 1]lines = [line.strip() for line in file_content.splitlines() if line.strip()]
                
               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
               [cite: 1]cursor = conn.cursor()
               [cite: 1]recovered_count = 0
               [cite: 1]for line in lines:
                   [cite: 1]numbers = re.findall(r'\d+(?:\.\d+)?', line)
                   [cite: 1]if len(numbers) >= 2:
                        [cite: 1]try:
                           [cite: 1]target_uid, balance_amount = int(numbers[0]), float(numbers[1])
                           [cite: 1]cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (target_uid,))
                           [cite: 1]if not cursor.fetchone():
                               [cite: 1]cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_uid, "User", balance_amount))
                           [cite: 1]else:
                               [cite: 1]cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (balance_amount, target_uid))
                           [cite: 1]conn.commit()
                           [cite: 1]recovered_count += 1
                            [cite: 1]try:
                               [cite: 1]bot.send_message(target_uid, f"{pe('deposit_success')} <b>ব্যালেন্স রিকভারি আপডেট!</b>\n\nআপনার একাউন্টে পূর্বের <b>৳{balance_amount}</b> জমা দেওয়া হয়েছে!", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                           [cite: 1]except Exception: pass
                       [cite: 1]except ValueError: pass
                
               [cite: 1]conn.close()
               [cite: 1]del admin_states[user_id]
               [cite: 1]bot.reply_to(message, f"{pe('step_tick')} রিকভারি সম্পূর্ণ হয়েছে! মোট <b>{recovered_count} জন</b> ইউজারের ব্যালেন্স সফলভাবে ব্যাক করা হয়েছে।", parse_mode="HTML")
           [cite: 1]except Exception as e:
               [cite: 1]bot.reply_to(message, f"ফাইল প্রসেস করতে ত্রুটি ঘটেছে: {e}")
           [cite: 1]return

       [cite: 1]elif action == "waiting_analysis_txt_for_broadcast":
            [cite: 1]try:
               [cite: 1]file_info = bot.get_file(message.document.file_id)
               [cite: 1]downloaded_file = bot.download_file(file_info.file_path)
               [cite: 1]file_content = downloaded_file.decode('utf-8', errors='ignore')
                
               [cite: 1]found_ids = re.findall(r'\b\d{6,12}\b', file_content)
               [cite: 1]target_user_ids = list(set([int(uid) for uid in found_ids]))

               [cite: 1]if not target_user_ids:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} ফাইল থেকে কোনো ইউজারের সঠিক আইডি খুঁজে পাওয়া যায়নি।", parse_mode="HTML")
                   [cite: 1]return

                [cite: 1]admin_states[user_id] = {
                   [cite: 1]"action": "waiting_live_broadcast_message",
                   [cite: 1]"target_uids": target_user_ids
                }

               [cite: 1]bot.reply_to(
                    [cite: 1]message,
                   [cite: 1]f"{pe('step_tick')} ফাইল ডিটেকশন সফল হয়েছে! মোট <b>{len(target_user_ids)} জন</b> ইউজার পাওয়া গেছে。\n\n"
                   [cite: 1]f"{pe('list_point')} <b>আপনি সবার উদ্দেশ্যে কি পাঠাতে চান?</b>\n"
                   [cite: 1]f"(টেক্সট, ছবি, ভয়েস মেসেজ, ভিডিও বা ফাইল সরাসরি পাঠিয়ে দিন):",
                   [cite: 1]parse_mode="HTML"
                )
           [cite: 1]except Exception as e:
               [cite: 1]bot.reply_to(message, f"ফাইল পড়তে সমস্যা হয়েছে: {e}")
           [cite: 1]return

# ----------------- সমস্ত মেসেজ ও ডিপোজিট ফ্লো হ্যান্ডলার -----------------
[cite: 1]def process_deposit_submission(message, file_id, is_document=False):
   [cite: 1]update_owner_premium_status(message.from_user)
   [cite: 1]user_id = message.from_user.id
   [cite: 1]raw_first_name = message.from_user.first_name or "N/A"
   [cite: 1]raw_username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
    
   [cite: 1]first_name = html.escape(raw_first_name)
   [cite: 1]username = html.escape(raw_username)
    
   [cite: 1]save_user_id_to_file(user_id)

   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (raw_username, user_id))
   [cite: 1]conn.commit()
   [cite: 1]conn.close()

   [cite: 1]if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
       [cite: 1]data = user_temp_deposit[user_id]
       [cite: 1]amount = data.get("amount", 0.0)
       [cite: 1]raw_trx = str(data.get("trx_id", "N/A"))
       [cite: 1]trx_id = html.escape(raw_trx)
       [cite: 1]method = html.escape(str(data.get("method", "Payment")))

       [cite: 1]bot.reply_to(
           [cite: 1]message,
           [cite: 1]f"{pe('waiting_clock')} <b>প্রিয় কাস্টমার দয়া করে ২ - ৩ মিনিট অপেক্ষা করুন, অ্যাকাউন্টে টাকা যোগ হচ্ছে...</b>",
           [cite: 1]parse_mode="HTML",
            [cite: 1]reply_markup=get_permanent_keyboard(user_id)
        )

       [cite: 1]req_id = str(uuid.uuid4())[:8]
       [cite: 1]pending_deposits[req_id] = {
           [cite: 1]"user_id": user_id,
           [cite: 1]"amount": amount,
           [cite: 1]"trx_id": raw_trx,
           [cite: 1]"method": method
        }
       [cite: 1]del user_temp_deposit[user_id]

       [cite: 1]admin_markup = InlineKeyboardMarkup()
       [cite: 1]admin_markup.add(
           [cite: 1]premium_inline_button("✅ Approve", "approve_btn", callback_data=f"app_{req_id}"),
           [cite: 1]premium_inline_button("❌ Reject", "reject_btn", callback_data=f"rej_{req_id}")
        )

        [cite: 1]caption_text = (
           [cite: 1]f"{pe('alarm_bell')} <b>New Payment Request Received!</b>\n\n"
           [cite: 1]f"{pe('profile_user')} <b>Name:</b> <b>{first_name}</b>\n"
           [cite: 1]f"{pe('username_link')} <b>Username:</b> <b>{username}</b>\n"
           [cite: 1]f"{pe('id_badge')} <b>User ID:</b> <code>{user_id}</code>\n"
           [cite: 1]f"{pe('deposit_money')} <b>Amount:</b> <b>৳{amount}</b>\n"
           [cite: 1]f"{pe('sendmoney_shield')} <b>Payment Method:</b> <b>{method}</b>\n"
           [cite: 1]f"{pe('trx_input')} <b>TrxID:</b> <code>{trx_id}</code>\n\n"
           [cite: 1]f"Please verify payment and take action below:"
        )

       [cite: 1]for i in range(3):
           [cite: 1]try:
               [cite: 1]bot.send_message(
                   [cite: 1]ADMIN_ID, 
                   [cite: 1]f"{pe('alarm_bell')} <b>[ALARM {i+1}/3] নতুন ডিপোজিট ও পেমেন্ট এসেছে! দ্রুত এপ্রুভ করুন। টং টং! 🛎️🔔</b>", 
                   [cite: 1]parse_mode="HTML"
                )
               [cite: 1]time.sleep(0.3)
           [cite: 1]except Exception:
               [cite: 1]pass

       [cite: 1]sent_successfully = False
       [cite: 1]try:
           [cite: 1]if not is_document:
               [cite: 1]bot.send_photo(ADMIN_ID, file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
           [cite: 1]else:
               [cite: 1]bot.send_document(ADMIN_ID, file_id, caption=caption_text, parse_mode="HTML", reply_markup=admin_markup)
           [cite: 1]sent_successfully = True
       [cite: 1]except Exception as e:
           [cite: 1]print(f"Error sending photo to admin: {e}")

       [cite: 1]if not sent_successfully:
           [cite: 1]try:
               [cite: 1]bot.send_message(ADMIN_ID, caption_text, parse_mode="HTML", reply_markup=admin_markup)
           [cite: 1]except Exception:
                [cite: 1]plain_text = f"New Deposit Received!\nUser ID: {user_id}\nAmount: {amount}\nTrxID: {raw_trx}\nMethod: {method}"
               [cite: 1]bot.send_message(ADMIN_ID, plain_text, reply_markup=admin_markup)

[cite: 1]@bot.message_handler(content_types=['text', 'photo', 'voice', 'audio', 'video', 'document'])
[cite: 1]def handle_all_messages_and_broadcast(message):
   [cite: 1]update_owner_premium_status(message.from_user)
   [cite: 1]user_id = message.from_user.id
   [cite: 1]username = f"@{message.from_user.username}" if message.from_user.username else "N/A"
   [cite: 1]save_user_id_to_file(user_id)

   [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
   [cite: 1]cursor = conn.cursor()
   [cite: 1]cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
   [cite: 1]conn.commit()
   [cite: 1]conn.close()

   [cite: 1]if user_id == ADMIN_ID and user_id in admin_states:
       [cite: 1]state_data = admin_states[user_id]
       [cite: 1]action = state_data.get("action")

       [cite: 1]if action == "waiting_live_broadcast_message":
           [cite: 1]target_uids = state_data["target_uids"]
           [cite: 1]del admin_states[user_id]

           [cite: 1]bot.reply_to(message, f"{pe('waiting_clock')} <b>মেম্বারদের কাছে বার্তা পাঠানো শুরু হচ্ছে... দয়া করে কিছুক্ষণ অপেক্ষা করুন।</b>", parse_mode="HTML")

           [cite: 1]success_count = 0
           [cite: 1]for target_uid in target_uids:
               [cite: 1]try:
                   [cite: 1]if message.content_type == 'text':
                       [cite: 1]bot.send_message(target_uid, f"{pe('loudspeaker')} <b>বিশেষ বার্তা:</b>\n\n{message.text}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                   [cite: 1]elif message.content_type == 'photo':
                       [cite: 1]cap = message.caption or ""
                       [cite: 1]bot.send_photo(target_uid, message.photo[-1].file_id, caption=f"{pe('loudspeaker')} <b>বিশেষ বার্তা:</b>\n\n{cap}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                   [cite: 1]elif message.content_type == 'voice':
                       [cite: 1]bot.send_voice(target_uid, message.voice.file_id, caption=f"{pe('loudspeaker')} <b>অফিসিয়াল ভয়েস বার্তা</b>", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                    [cite: 1]elif message.content_type == 'video':
                       [cite: 1]cap = message.caption or ""
                       [cite: 1]bot.send_video(target_uid, message.video.file_id, caption=f"{pe('loudspeaker')} <b>বিশেষ ভিডিও:</b>\n\n{cap}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                   [cite: 1]elif message.content_type == 'document':
                       [cite: 1]bot.send_document(target_uid, message.document.file_id, caption=f"{pe('loudspeaker')} <b>অফিসিয়াল ফাইল</b>", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_uid))
                   [cite: 1]success_count += 1
               [cite: 1]except Exception:
                   [cite: 1]pass

           [cite: 1]bot.send_message(
               [cite: 1]ADMIN_ID,
               [cite: 1]f"{pe('step_tick')} <b>ব্রডকাস্ট সম্পূর্ণ সফল হয়েছে!</b>\n"
               [cite: 1]f"মোট পাঠানো হয়েছে: <b>{success_count} জন</b> মেম্বারের ইনবক্সে।",
               [cite: 1]parse_mode="HTML"
            )
           [cite: 1]return

   [cite: 1]if message.content_type == 'photo':
       [cite: 1]if user_id in user_temp_deposit and user_temp_deposit[user_id].get("step") == "waiting_screenshot":
           [cite: 1]photo_id = message.photo[-1].file_id
           [cite: 1]process_deposit_submission(message, photo_id, is_document=False)
           [cite: 1]return

   [cite: 1]if message.content_type != 'text':
       [cite: 1]return

   [cite: 1]text = message.text

   [cite: 1]if not check_user_subscription(user_id):
       [cite: 1]not_joined_msg = get_setting_msg('not_joined_msg', f"{pe('warn_icon')} আপনি এখনো আমাদের চ্যানেলে জয়েন করেননি!")
       [cite: 1]bot.send_message(message.chat.id, not_joined_msg, parse_mode="HTML", reply_markup=get_force_sub_markup())
       [cite: 1]return

   [cite: 1]if user_id in user_temp_deposit:
       [cite: 1]state = user_temp_deposit[user_id].get("step")

       [cite: 1]if state == "waiting_amount":
           [cite: 1]try:
               [cite: 1]amount = float(text)
               [cite: 1]if amount < 10 or amount > 10000:
                   [cite: 1]bot.send_message(user_id, f"{pe('warn_icon')} সর্বনিম্ন ১০ টাকা এবং সর্বোচ্চ ১০,০০০ টাকা ডিপোজিট করতে পারবেন। সঠিক পরিমাণ দিন:", parse_mode="HTML")
                   [cite: 1]return
               [cite: 1]user_temp_deposit[user_id]["amount"] = amount
               [cite: 1]user_temp_deposit[user_id]["step"] = "waiting_method"
               [cite: 1]bot.send_message(user_id, f"{pe('sendmoney_shield')} <b>আপনি কিসের মাধ্যমে পেমেন্ট করতে চাচ্ছেন সিলেক্ট করুন:</b>", parse_mode="HTML", reply_markup=get_payment_method_markup())
               [cite: 1]return
           [cite: 1]except ValueError:
               [cite: 1]bot.send_message(user_id, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 50 বা 500)।", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
               [cite: 1]return

       [cite: 1]elif state == "waiting_trx":
           [cite: 1]user_temp_deposit[user_id]["trx_id"] = text.strip()
           [cite: 1]user_temp_deposit[user_id]["step"] = "waiting_screenshot"
           [cite: 1]bot.send_message(
               [cite: 1]user_id,
               [cite: 1]f"{pe('step_tick')} <b>ধন্যবাদ! আপনার ট্রানজেকশন আইডি গ্রহণ করা হয়েছে।</b>\n\n"
               [cite: 1]f"{pe('camera_icon')} এখন পেমেন্টের একটি স্ক্রিনশট (Screenshot) এই চ্যাটে পাঠান:",
               [cite: 1]parse_mode="HTML",
               [cite: 1]reply_markup=get_permanent_keyboard(user_id)
            )
           [cite: 1]return

       [cite: 1]elif state == "waiting_service_username":
           [cite: 1]data = user_temp_deposit[user_id]
           [cite: 1]cat_id, sub_name, price, username_input = data["cat_id"], data["sub_name"], data["price"], text.strip()
            [cite: 1]del user_temp_deposit[user_id]

           [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
           [cite: 1]cursor = conn.cursor()
           [cite: 1]cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
           [cite: 1]bal_res = cursor.fetchone()
           [cite: 1]current_bal = bal_res[0] if bal_res else 0.0

           [cite: 1]if current_bal < price:
                [cite: 1]conn.close()
               [cite: 1]bot.send_message(user_id, f"{pe('insufficient_bal')} আপনার একাউন্টে পর্যাপ্ত ব্যালেন্স নেই!", parse_mode="HTML", reply_markup=get_permanent_keyboard(user_id))
               [cite: 1]return

           [cite: 1]new_bal = current_bal - price
           [cite: 1]cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_bal, user_id))
           [cite: 1]conn.commit()
           [cite: 1]conn.close()

           [cite: 1]emoji_k = "telegram_premium_cat" if "telegram" in cat_id else get_vpn_emoji_key(sub_name)
           [cite: 1]bot.send_message(
               [cite: 1]user_id,
               [cite: 1]f"{pe('order_pending')} আপনার অর্ডারটি সফলভাবে সাবমিট হয়েছে!\n\n"
               [cite: 1]f"{pe(emoji_k)} সার্ভিস: <b>{sub_name}</b> {pe(emoji_k)}\n"
               [cite: 1]f"{pe('profile_user')} ইউজারনেম/আইডি: <code>{username_input}</code>\n"
               [cite: 1]f"{pe('money_spent')} পরিশোধিত মূল্য: ৳{price}\n"
               [cite: 1]f"{pe('wallet_balance')} অবশিষ্ট ব্যালেন্স: ৳{new_bal}\n\n"
               [cite: 1]f"{pe('waiting_clock')} দয়া করে কিছুক্ষণ অপেক্ষা করুন, অ্যাডমিন খুব শীঘ্রই আপনার সার্ভিসটি কমপ্লিট করে দেবেন।",
               [cite: 1]parse_mode="HTML",
               [cite: 1]reply_markup=get_permanent_keyboard(user_id)
            )

           [cite: 1]admin_markup = InlineKeyboardMarkup()
           [cite: 1]admin_markup.add(premium_inline_button("✅ Complete Order & Deliver", "approve_btn", callback_data=f"complete_order_{user_id}"))

           [cite: 1]admin_order_msg = (
               [cite: 1]f"{pe('alarm_bell')} <b>New Order Received!</b>\n\n"
               [cite: 1]f"{pe('profile_user')} <b>User ID:</b> <code>{user_id}</code>\n"
               [cite: 1]f"{pe('box_package')} <b>Service:</b> <b>{sub_name}</b>\n"
               [cite: 1]f"{pe('username_link')} <b>Target Account:</b> <code>{username_input}</code>\n"
                [cite: 1]f"{pe('money_spent')} <b>Price:</b> ৳{price}"
            )
           [cite: 1]bot.send_message(ADMIN_ID, admin_order_msg, parse_mode="HTML", reply_markup=admin_markup)
           [cite: 1]return

       [cite: 1]elif state == "waiting_custom_qty":
           [cite: 1]cat_id = user_temp_deposit[user_id]["cat_id"]
           [cite: 1]try:
               [cite: 1]qty = int(text)
               [cite: 1]if qty <= 0:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক পিস সংখ্যা লিখুন.", parse_mode="HTML")
                   [cite: 1]return
               [cite: 1]del user_temp_deposit[user_id]
               [cite: 1]process_purchase(message.chat.id, user_id, cat_id, qty)
               [cite: 1]return
           [cite: 1]except ValueError:
               [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দয়া করে শুধু সংখ্যা লিখে পাঠান।", parse_mode="HTML")
               [cite: 1]return

    # অ্যাডমিন প্যানেল অ্যাকশনস
   [cite: 1]if user_id == ADMIN_ID and user_id in admin_states:
       [cite: 1]state_data = admin_states[user_id]
       [cite: 1]action = state_data.get("action")

       [cite: 1]if action == "adding_new_cat":
           [cite: 1]parts = text.rsplit(maxsplit=1)
           [cite: 1]if len(parts) == 2:
               [cite: 1]name, price_str = parts[0], parts[1].replace('৳', '').strip()
               [cite: 1]try:
                   [cite: 1]price = float(price_str)
                   [cite: 1]admin_states[user_id] = {"pending_btn_data": {"mode": "new_cat", "name": name, "price": price}}
                   [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
                   [cite: 1]markup.add(
                       [cite: 1]premium_inline_button("✅ Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                       [cite: 1]premium_inline_button("❌ No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                   [cite: 1]bot.reply_to(message, f"<b>{name}</b> (৳{price})\n\nআপনি কি এই বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                   [cite: 1]return
               [cite: 1]except ValueError:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দাম সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                   [cite: 1]return

       [cite: 1]elif action == "editing_cat":
           [cite: 1]cat_id = state_data["cat_id"]
           [cite: 1]parts = text.rsplit(maxsplit=1)
           [cite: 1]if len(parts) == 2:
               [cite: 1]name, price_str = parts[0], parts[1].replace('৳', '').strip()
               [cite: 1]try:
                   [cite: 1]price = float(price_str)
                   [cite: 1]admin_states[user_id] = {"pending_btn_data": {"mode": "edit_cat", "cat_id": cat_id, "name": name, "price": price}}
                   [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
                   [cite: 1]markup.add(
                       [cite: 1]premium_inline_button("✅ Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                       [cite: 1]premium_inline_button("❌ No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                   [cite: 1]bot.reply_to(message, f"<b>{name}</b> (৳{price})\n\nআপনি কি এই বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                   [cite: 1]return
               [cite: 1]except ValueError:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দামটি সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                   [cite: 1]return

       [cite: 1]elif action == "adding_sub_item":
           [cite: 1]cat_id = state_data["cat_id"]
           [cite: 1]parts = text.rsplit(maxsplit=1)
           [cite: 1]if len(parts) == 2:
                [cite: 1]sub_name, price_str = parts[0], parts[1].replace('৳', '').strip()
               [cite: 1]try:
                   [cite: 1]price = float(price_str)
                   [cite: 1]admin_states[user_id] = {"pending_btn_data": {"mode": "new_sub", "cat_id": cat_id, "name": sub_name, "price": price}}
                   [cite: 1]markup = InlineKeyboardMarkup(row_width=2)
                   [cite: 1]markup.add(
                       [cite: 1]premium_inline_button("✅ Yes (Add Emoji)", "approve_btn", callback_data="btn_emojichoice_yes"),
                       [cite: 1]premium_inline_button("❌ No (Text Only)", "reject_btn", callback_data="btn_emojichoice_no")
                    )
                   [cite: 1]bot.reply_to(message, f"<b>{sub_name}</b> (৳{price})\n\nআপনি কি এই প্যাকেজ বাটনে প্রিমিয়াম ইমোজি যুক্ত করতে চান?", parse_mode="HTML", reply_markup=markup)
                   [cite: 1]return
               [cite: 1]except ValueError:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দাম সঠিক সংখ্যায় দিন।", parse_mode="HTML")
                   [cite: 1]return

       [cite: 1]elif action == "waiting_member_uid_for_balance":
           [cite: 1]state_data["target_uid"] = text.strip()
           [cite: 1]state_data["action"] = "waiting_member_amount_for_balance"
           [cite: 1]bot.reply_to(message, f"{pe('deposit_money')} এখন এই ইউজারের অ্যাকাউন্টে কত টাকা ব্যাক দিতে চাচ্ছেন? সঠিক পরিমাণ (যেমন: <code>50</code> বা <code>0.09</code>) চ্যাটে লিখে পাঠান:", parse_mode="HTML")
            [cite: 1]return

       [cite: 1]elif action == "waiting_member_amount_for_balance":
           [cite: 1]target_uid_str = state_data["target_uid"]
           [cite: 1]del admin_states[user_id]
           [cite: 1]try:
               [cite: 1]target_uid = int(target_uid_str)
               [cite: 1]add_amount = float(text.strip())

               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
                [cite: 1]cursor = conn.cursor()
               [cite: 1]cursor.execute("SELECT user_id, balance FROM users WHERE user_id = ?", (target_uid,))
               [cite: 1]user_row = cursor.fetchone()

               [cite: 1]if user_row:
                   [cite: 1]cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (add_amount, target_uid))
                   [cite: 1]conn.commit()
                   [cite: 1]cursor.execute("SELECT balance FROM users WHERE user_id = ?", (target_uid,))
                   [cite: 1]new_bal = cursor.fetchone()[0]
               [cite: 1]else:
                   [cite: 1]cursor.execute("INSERT INTO users (user_id, first_name, balance, username) VALUES (?, ?, ?, 'N/A')", (target_uid, "User", add_amount))
                   [cite: 1]conn.commit()
                   [cite: 1]new_bal = add_amount
               [cite: 1]conn.close()

               [cite: 1]try:
                    [cite: 1]bot.send_message(
                       [cite: 1]target_uid,
                       [cite: 1]f"{pe('deposit_success')} <b>বট আপডেট করা হয়েছে!</b>\n\nআপনার একাউন্টে পূর্বের পাওনা ৳{add_amount} টাকা এড করা হয়েছে। এখন আপনারা কেনাকাটা করতে পারেন!",
                       [cite: 1]parse_mode="HTML",
                        [cite: 1]reply_markup=get_permanent_keyboard(target_uid)
                    )
               [cite: 1]except Exception:
                   [cite: 1]pass

               [cite: 1]bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজার (<code>{target_uid}</code>) এর অ্যাকাউন্টে ব্যালেন্স <b>৳{add_amount}</b> যোগ করা হয়েছে! নতুন ব্যালেন্স: ৳{new_bal}", parse_mode="HTML")
           [cite: 1]except ValueError:
               [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} ইউজার আইডি অথবা টাকার পরিমাণ সঠিক সংখ্যায় দিন। পুনরায় অ্যাডমিন প্যানেল থেকে চেষ্টা করুন।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]elif action == "waiting_member_uid_for_remove_money":
           [cite: 1]target_uid_str = text.strip()
           [cite: 1]try:
               [cite: 1]target_uid = int(target_uid_str)
               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
               [cite: 1]cursor = conn.cursor()
               [cite: 1]cursor.execute("SELECT balance, first_name FROM users WHERE user_id = ?", (target_uid,))
               [cite: 1]row = cursor.fetchone()
               [cite: 1]conn.close()

               [cite: 1]if row:
                   [cite: 1]current_bal = row[0]
                   [cite: 1]u_name = row[1] or "User"
                    [cite: 1]state_data["target_uid"] = target_uid
                   [cite: 1]state_data["action"] = "waiting_member_amount_for_remove_money"
                    [cite: 1]bot.reply_to(message, f"{pe('profile_user')} ইউজার: <b>{u_name}</b> (ID: <code>{target_uid}</code>)\nবর্তমান ব্যালেন্স: <b>৳{current_bal}</b>\n\nএখন আপনি ওনার অ্যাকাউন্টে কত টাকা রাখতে চাচ্ছেন (বা কত টাকা করতে চাচ্ছেন) সেটির সঠিক পরিমাণ চ্যাটে লিখে পাঠান:", parse_mode="HTML")
               [cite: 1]else:
                   [cite: 1]del admin_states[user_id]
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} এই ইউজার আইডি দিয়ে ডাটাবেজে কোনো রেকর্ড পাওয়া যায়নি।", parse_mode="HTML")
            [cite: 1]except ValueError:
               [cite: 1]del admin_states[user_id]
               [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যায় ইউজার আইডি দিন।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]elif action == "waiting_member_amount_for_remove_money":
           [cite: 1]target_uid = state_data["target_uid"]
           [cite: 1]del admin_states[user_id]
           [cite: 1]try:
               [cite: 1]new_amount = float(text.strip())
                [cite: 1]if new_amount < 0:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} টাকার পরিমাণ ঋণাত্মক হতে পারে না।", parse_mode="HTML")
                   [cite: 1]return

               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
               [cite: 1]cursor = conn.cursor()
               [cite: 1]cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_amount, target_uid))
               [cite: 1]conn.commit()
               [cite: 1]conn.close()

               [cite: 1]try:
                   [cite: 1]bot.send_message(
                       [cite: 1]target_uid,
                       [cite: 1]f"{pe('deposit_success')} <b>অ্যাকাউন্ট ব্যালেন্স আপডেট হয়েছে!</b>\n\nআপনার একাউন্টের বর্তমান ব্যালেন্স এডজাস্ট করে <b>৳{new_amount}</b> নির্ধারণ করা হয়েছে।",
                       [cite: 1]parse_mode="HTML",
                       [cite: 1]reply_markup=get_permanent_keyboard(target_uid)
                    )
               [cite: 1]except Exception:
                   [cite: 1]pass

               [cite: 1]bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজার (<code>{target_uid}</code>)-এর অ্যাকাউন্ট ব্যালেন্স এডিট করে <b>৳{new_amount}</b> করা হয়েছে!", parse_mode="HTML")
           [cite: 1]except ValueError:
               [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} টাকার পরিমাণ সঠিক সংখ্যায় দিন।", parse_mode="HTML")
           [cite: 1]return

        [cite: 1]elif action == "searching_user":
           [cite: 1]del admin_states[user_id]
           [cite: 1]target_id_str = text.strip()
           [cite: 1]try:
               [cite: 1]target_uid = int(target_id_str)
               [cite: 1]conn = sqlite3.connect("shop_bot.db", timeout=30)
               [cite: 1]cursor = conn.cursor()
               [cite: 1]cursor.execute("SELECT user_id, first_name, balance, username FROM users WHERE user_id = ?", (target_uid,))
               [cite: 1]user_row = cursor.fetchone()
               [cite: 1]conn.close()
               [cite: 1]if user_row:
                   [cite: 1]u_id, u_name, u_bal, u_user = user_row
                   [cite: 1]resp = (
                       [cite: 1]f"{pe('profile_user')} <b>User Profile & Details:</b>\n\n"
                       [cite: 1]f"{pe('profile_user')} <b>Name:</b> {u_name or 'User'}\n"
                       [cite: 1]f"{pe('username_link')} <b>Username:</b> <b>{u_user or 'N/A'}</b>\n"
                       [cite: 1]f"{pe('id_badge')} <b>User ID:</b> <code>{u_id}</code>\n"
                       [cite: 1]f"{pe('balance_coin')} <b>Account Balance:</b> <b>৳{u_bal}</b> {pe('diamond_badge')}"
                    )
                   [cite: 1]bot.reply_to(message, resp, parse_mode="HTML")
               [cite: 1]else:
                   [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} এই ইউজার আইডি দিয়ে কোনো রেকর্ড পাওয়া যায়নি।", parse_mode="HTML")
           [cite: 1]except ValueError:
               [cite: 1]bot.reply_to(message, f"{pe('warn_icon')} দয়া করে সঠিক সংখ্যায় ইউজার আইডি দিন।", parse_mode="HTML")
           [cite: 1]return

       [cite: 1]elif action == "waiting_delivery_content":
           [cite: 1]target_user = state_data["target_user"]
           [cite: 1]del admin_states[user_id]
           [cite: 1]try:
               [cite: 1]bot.send_message(target_user, f"{pe('order_delivered')} <b>আপনার অর্ডারটি সফলভাবে সম্পন্ন হয়েছে!</b>\n\n{pe('box_package')} <b>ডিটেইলস / অ্যাকাউন্ট:</b>\n{text}\n\nআমাদের সাথে থাকার জন্য ধন্যবাদ! {pe('welcome_heart')}", parse_mode="HTML", reply_markup=get_permanent_keyboard(target_user))
               [cite: 1]bot.reply_to(message, f"{pe('step_tick')} সফলভাবে ইউজারের কাছে (ID: <code>{target_user}</code>) অর্ডার ডেলিভারি পাঠানো হয়েছে!", parse_mode="HTML")
           [cite: 1]except Exception as e:
               [cite: 1]bot.reply_to(message, f"ইউজারের কাছে মেসেজ পাঠানো যায়নি: {e}")
           [cite: 1]return

# ----------------- Web Server & Polling -----------------
[cite: 1]app = Flask(__name__)

[cite: 1]@app.route('/')
[cite: 1]def home():
   [cite: 1]return "Bot is running successfully!"

[cite: 1]if __name__ == "__main__":
   [cite: 1]port = int(os.environ.get("PORT", 10000))
    
   [cite: 1]def run_bot():
       [cite: 1]while True:
           [cite: 1]try:
               [cite: 1]bot.remove_webhook()
               [cite: 1]bot.infinity_polling(none_stop=True, interval=0, timeout=20, long_polling_timeout=20)
           [cite: 1]except Exception as e:
               [cite: 1]print(f"Polling crashed: {e}")
               [cite: 1]time.sleep(1)
        
   [cite: 1]t_bot = threading.Thread(target=run_bot)
   [cite: 1]t_bot.start()
    
   [cite: 1]t_backup = threading.Thread(target=auto_drive_backup_loop, daemon=True)
   [cite: 1]t_backup.start()
    
   [cite: 1]app.run(host="0.0.0.0", port=port)
