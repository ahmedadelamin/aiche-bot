import logging
import os
import asyncio
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request

# ========= CONFIG =========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PYTHONANYWHERE_USERNAME = os.environ.get("PA_USERNAME", "AmirEhab")
WEBHOOK_URL = f"https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com/{BOT_TOKEN}"
ADMIN_ID = 1846962771
USERS_FILE = "/home/AmirEhab/users.json"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ========= USER STORAGE =========
import threading
user_lock = threading.Lock()

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
    except Exception as e:
        logger.error(f"Error loading users: {e}")
    return set()

def save_user(user_id):
    try:
        with user_lock:
            users = load_users()
            if user_id not in users:
                users.add(user_id)
                with open(USERS_FILE, "w") as f:
                    json.dump(list(users), f)
    except Exception as e:
        logger.error(f"Error saving user: {e}")

# ========= MENUS =========
main_menu = [["Know AIChE"], ["AIChE Technical Products"], ["Academic"]]
know_aiche_menu = [["Who Are We?"], ["Our Vision", "Our Mission"], ["AIChE''s Official Accounts on Social Media"], ["AIChE''s Mega Events"], ["AIChE''s Main Sponsor"], ["⬅️ Back", "🏠 Main Menu"]]
tech_products_menu = [["ATB", "Spark"], ["Capsules", "Library"], ["⬅️ Back", "🏠 Main Menu"]]
academic_levels_menu = [["Level 1", "Level 2"], ["Level 3", "Level 4"], ["⬅️ Back", "🏠 Main Menu"]]
semester_menu = [["Semester 1"], ["Semester 2"], ["⬅️ Back", "🏠 Main Menu"]]

subjects = {
    "Level 1": ["Introduction to Petroleum Refining", "Fundamentals of Chemical Engineering", "Organic Chemistry"],
    "Level 2": ["Petroleum Refining Engineering 1", "Crude Oil Evaluation", "Unit Operation 1", "Water Treatment"],
    "Level 3 - Semester 1": ["Unit Operation 2", "Reactions", "Corrosion", "Introduction to Petroleum Engineering", "Petrochemicals 1"],
    "Level 3 - Semester 2": ["Computer Applications", "Heat Transfer", "Petroleum Products Testing", "HYSYS", "Storage and Transportation", "Unit Processes"],
    "Level 4 - Semester 1": ["Plant Design", "Pollution Control", "Design of Refining Equipment", "Process Control", "Petroleum Refining 2", "Operation Research in Chemical Engineering"],
    "Level 4 - Semester 2": ["Furnace Design", "Petrochemicals 2", "Process Design", "Gas Engineering"]
}

SUBJECT_FILE_IDS = {
    "Introduction to Petroleum Refining": "BQACAgQAAxkBAAIDyWj6LZsAAe2QrQTY_z2R6rWTNCgwyAACuBsAArWs0VOP-RJ2LEIkazYE",
    "Fundamentals of Chemical Engineering": "BQACAgQAAxkBAAIDy2j6LzphWLCUV16D8CCyVw-4w5d7AAK6GwACtazRU9mz3a_ClI3pNgQ",
    "Organic Chemistry": "BQACAgQAAxkBAAIDzWj6MN3TgCodHYtFsLuEWcaazxEwAAK9GwACtazRUzl_L47oaJ9BNgQ",
    "Petroleum Refining Engineering 1": "BQACAgQAAxkBAAID0Wj6OWeqjdZdepJur5gVtVG_Om66AALUGwACtazRU0FrkAxKoOonNgQ",
    "Crude Oil Evaluation": "BQACAgQAAxkBAAID1Wj6RdsK8q3mc8TuPjNnPfHgoJQEAAJjGwACtazZU2jidsW-aBnRNgQ",
    "Unit Operation 1": "BQACAgQAAxkBAAID02j6OcE4SnIW1luTGO0_XytuzvhBAALZGwACtazRU2ziCFv8B9_XNgQ",
    "Water Treatment": "BQACAgQAAxkBAAIDz2j6MgI0y-DngmZIn8U7kmV9uo-rAAK-GwACtazRU8oLdizZJY7tNgQ",
    "Unit Operation 2": "BQACAgQAAxkBAAID22j6Vw02RCHVpAeCmsKAiBJzEMWlAALyGwACtazZU9FgKQ2_bbwiNgQ",
    "Reactions": "BQACAgQAAxkBAAID42j6aV-XiuGb_TeqmWOaX4bAJb2AAAK_HAACtazZUxqVwmKY6yuANgQ",
    "Corrosion": "BQACAgQAAxkBAAID2Wj6VB0YvBFK-KOgcTBbSXiLjsCaAAKZGwACtazZU-u4MOC0BthwNgQ",
    "Introduction to Petroleum Engineering": "BQACAgQAAxkBAAID4Wj6ZB9UjgABO9nfXD32GEJ8X9wMhgACoRwAArWs2VN0JR-TqlYZ3TYE",
    "Petrochemicals 1": "BQACAgQAAxkBAAID12j6UISYOEM-Y3yrPBBhmvIDhnOcAAJ7GwACtazZUz3sciWfXBFqNgQ",
    "Pollution Control": "BQACAgQAAxkBAAIEMGj6htGrVDyS1LGcpMRhCM40DC27AAIVHQACtazZU5vHYi6wWKCANgQ",
    "Process Control": "BQACAgQAAxkBAAIEMmj6h14gIRcBY398nrnf_BMMsOgFAAIaHQACtazZU2ppaLmqJ7OKNgQ",
    "Operation Research in Chemical Engineering": "BQACAgQAAxkBAAIENGj6iGMT4M5fekIvsjxHfgLDtPGWAAIdHQACtazZU778VI4cIV0ZNgQ",
    "Storage and Transportation": "BQACAgQAAxkBAAIENmj6ikOYsq86sxEFbJDoUApK1-BhAAIfHQACtazZU9spjtWfeZgTNgQ",
    "HYSYS": "BQACAgQAAxkBAAIEOGj6kFO4j2vDlwg2nzVH_o4ToIRRAAInHQACtazZU_Xcf7KfDYvJNgQ",
    "Computer Applications": "BQACAgQAAxkBAAIEOmj6kzJJLtXk2BgCtJTiR2nIJae1AAJDHQACtazZUxnF5yR_TflfNgQ",
    "Heat Transfer": "BQACAgQAAxkBAAIEQGj6l4j7MLuBhBWs70JmTY2L5lNCAAJEHQACtazZU6vMulWD2eKMNgQ",
    "Design of Refining Equipment": "BQACAgQAAxkBAAIE5mj6zye5DtVbNyto2UKefA6nlsJ-AAJrHQACtazZU3CEjpt7ybggNgQ",
    "Plant Design": "BQACAgQAAxkBAAIE6Gj60aAySZct2wKT95_9UNF2dcOQAAJsHQACtazZU2bCZLI4-l2MNgQ",
    "Unit Processes": "BQACAgQAAxkBAAIE6mj60sqsrasNcvxBENddlISuDh2vAAJtHQACtazZU3Jz55-0_U88NgQ",
    "Petroleum Products Testing": "BQACAgQAAxkBAAIE7Gj61l5IS0-9vpkrYo14rxsV4-zqAAJvHQACtazZU3m5Mkp4g_gNNgQ",
    "Process Design": "BQACAgQAAxkBAAIE7mj62xkTFMbM1GCSTX_LvCwEBYaoAALoGgACBh_QUxDnsDQoa5zGNgQ",
    "Petroleum Refining 2": "BQACAgQAAxkBAAIE8Gj63EaVqt0u4dJw4zeJNFUgciPGAALqGgACBh_QU2aiZMRtu-8dNgQ",
    "Petrochemicals 2": "BQACAgQAAxkBAAIE8mj63j_T1OOYW4D0Qajy8s_CLVthAALrGgACBh_QU3W47ItXP_HZNgQ",
    "Gas Engineering": "BQACAgQAAxkBAAIFy2j7PrLdzqs3l9Rp9jINivbfm8EuAAJNGAACBh_YU8E6sVOOHYX2NgQ",
    "Furnace Design": "BQACAgQAAxkBAAIFzWj7SW9_Gn7eDYTYzhrJT5iiH5bNAAJUGAACBh_YUxW4yhPcKJBENgQ",
}

SUBJECT_CHANNELS = {
    "Introduction to Petroleum Refining": "https://t.me/+BM7qUVxqCWkwM2I0",
    "Fundamentals of Chemical Engineering": "https://t.me/+kFWVMp6UBAs2Y2Q0",
    "Organic Chemistry": "https://t.me/organic778",
    "Petroleum Refining Engineering 1": "https://t.me/refining_engineering",
    "Crude Oil Evaluation": "https://t.me/Crude_evaluation",
    "Unit Operation 1": "https://t.me/Unit_Operations1",
    "Water Treatment": "https://t.me/industrial_water_treatmen",
    "Unit Operation 2": "https://t.me/+77F5ioBTJZs3OWFk",
    "Reactions": "https://t.me/+jmaKu_xv2zJlYzZk",
    "Corrosion": "https://t.me/+AKVe-zJ2xIE2NGFk",
    "Introduction to Petroleum Engineering": "https://t.me/+1m_xD9ZjdH45OTU0",
    "Petrochemicals 1": "https://t.me/+yEOrH6gQEwM3ZDJk",
    "Pollution Control": "https://t.me/+_anxt75rM-9hZDg0",
    "Process Control": "https://t.me/+W3gF_ZzYplRjZTk0",
    "Operation Research in Chemical Engineering": "https://t.me/+NkrqGY1_zpBlZWI8",
    "Storage and Transportation": "https://t.me/+msNn5eZYCeE2NGI0",
    "HYSYS": "https://t.me/+EaF8J_jSaoMxMzc0",
    "Computer Applications": "https://t.me/+jsx4vJQb5PgxZjg8",
    "Heat Transfer": "https://t.me/+r1jJrVI_Ng45MTU0",
    "Design of Refining Equipment": "https://t.me/+8qqZ9VjdvIJhYmQ0",
    "Plant Design": "https://t.me/+g2kuiiTgu6YzZDNk",
    "Unit Processes": "https://t.me/+al83O_8c1uI4NTY0",
    "Petroleum Products Testing": "https://t.me/+QsVnbQxqxzZlM2Fk",
    "Process Design": "https://t.me/+Su665DAU77diYThk",
    "Petroleum Refining 2": "https://t.me/+jCeTtQRRVR40YmQ8",
    "Petrochemicals 2": "https://t.me/+DMGm6JSA_zUzOGI8",
    "Gas Engineering": "https://t.me/+jtS4f9INne1iYTE0",
    "Furnace Design": "https://t.me/+PsUmr6CLvAozMWNk"
}

IMAGE_FILE_IDS = {
    "who_we_are": "AgACAgQAAxkBAANIaTaq-Cehe23FurX3GFxL2W0ksLQAAvcLaxuIRLFRib46A75ZLDoBAAMCAAN5AAM2BA",
    "our_vision": "AgACAgQAAxkBAANKaTarCVMF7tFP2n64wdtuhwXBKaMAAvgLaxuIRLFRzc1h6-IWJOcBAAMCAAN5AAM2BA",
    "PGIE": "AgACAgQAAxkBAANGaTaputvh6rb5RMRtPnTi06jRrkoAAvYLaxuIRLFRvkkWz2Hh73oBAAMCAAN5AAM2BA",
    "Career Fair": "AgACAgQAAxkBAANBaTapr02nbieKjzsrJimdQ-ATnzwAAvQLaxuIRLFRSZXCxK-z_WIBAAMCAAN5AAM2BA",
    "AIChE Refining Diploma": "AgACAgQAAxkBAANDaTaprywhlqML1CbLpn1df1cv-l0AAvULaxuIRLFRlf5idOFYP38BAAMCAAN5AAM2BA",
    "Brain++": "AgACAgQAAxkBAAIFr2qZ3lJ-hhbCdsh5TZCRBD4NrbbnAAKrEmsbwzzRUGMF0_5ZXE1DAQADAgADeQADPQQ",
    "sponsor": "AgACAgQAAxkBAANMaTarVTZt0lSfdnHziXmFVe05Tm0AAvkLaxuIRLFRC7g3mpsf9bEBAAMCAAN5AAM2BA",
    "HYSYS Course": "AgACAgQAAxkBAAIFrGqZ3Ej0-mKl0nv9oAzfximI_VPZAAI7EWsb467RUMDLhias_X7bAQADAgADeAADPQQ",
    "Reforming Arena": "AgACAgQAAxkBAAIGHWqZ5Xd2UyJrz4uhlu1W_Sz5SQKkAAK0EmsbwzzRUMGJXH6H9r_5AQADAgADeAADPQQ",
    "ME Gathering": "AgACAgQAAxkBAAIGOWqZ5y8u_oN8nGFZL1_eo12ABT3NAAK2EmsbwzzRUOzmTz-0oEX7AQADAgADeAADPQQ",
    "Panel Discussion": "AgACAgQAAxkBAAIGPWqZ6EQzA2b1FqeL2q5qqTMHQv7nAAJLEWsb467RUBCGoX8eidXVAQADAgADeAADPQQ",
}

def escape_markdown(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# ========= HANDLERS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text("Welcome to AIChE Suez Chapter Bot! 👋\nPlease choose an option below:", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    name = escape_markdown(user.first_name or "User")
    await update.message.reply_text(
        f"👤 *Your Info:*\n\n"
        f"🔹 *Name:* {name}\n"
        f"🔹 *Telegram ID:* `{user.id}`",
        parse_mode="MarkdownV2"
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command!")
        return
        
    message = ""
    photo_id = None
    document_id = None
    
    # Handle text or caption
    if update.message.text and context.args:
        message = " ".join(context.args)
    elif update.message.caption:
        # Extract everything after /broadcast in caption
        caption = update.message.caption
        if "/broadcast" in caption:
            message = caption.split("/broadcast", 1)[1].strip()
            
    # Handle media
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
    elif update.message.document:
        document_id = update.message.document.file_id
        
    if not message and not photo_id and not document_id:
        await update.message.reply_text("📢 Usage:\n/broadcast Your message here\nOr send a photo/document with caption:\n/broadcast Your message here")
        return
        
    users = load_users()
    success, failed = 0, 0
    status_msg = await update.message.reply_text(f"⏳ Broadcasting to {len(users)} users...")
    
    for uid in users:
        try:
            formatted_msg = f"📢 *Message from AIChE Suez:*\n\n{message}" if message else "📢 *Message from AIChE Suez:*"
            if photo_id:
                await context.bot.send_photo(chat_id=uid, photo=photo_id, caption=formatted_msg, parse_mode="Markdown")
            elif document_id:
                await context.bot.send_document(chat_id=uid, document=document_id, caption=formatted_msg, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=uid, text=formatted_msg, parse_mode="Markdown")
            success += 1
        except Exception:
            failed += 1
            
    await status_msg.edit_text(f"✅ Broadcast Complete!\n\n👥 Total Users: {len(users)}\n✅ Successful: {success}\n❌ Failed: {failed}")

async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized!")
        return
    users = load_users()
    await update.message.reply_text(f"👥 Total Users: {len(users)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    if update.message.photo:
        await update.message.reply_text(f"🖼️ Image file_id:\n{update.message.photo[-1].file_id}")
    elif update.message.document:
        await update.message.reply_text(f"📄 Document file_id:\n{update.message.document.file_id}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    text = update.message.text
    if text == "Know AIChE":
        await update.message.reply_text("Learn more about AIChE 👇", reply_markup=ReplyKeyboardMarkup(know_aiche_menu, resize_keyboard=True))
    elif text == "AIChE Technical Products":
        await update.message.reply_text("Explore AIChE Technical Products 👇", reply_markup=ReplyKeyboardMarkup(tech_products_menu, resize_keyboard=True))
    elif text == "Academic":
        await update.message.reply_text("Choose your academic level 👇", reply_markup=ReplyKeyboardMarkup(academic_levels_menu, resize_keyboard=True))
    elif text == "Who Are We?":
        await update.message.reply_photo(IMAGE_FILE_IDS["who_we_are"], caption="🌐 *Who We Are*\nAIChE stands for American Institute of Chemical Engineers.", parse_mode="Markdown")
    elif text == "Our Mission":
        await update.message.reply_text(
            "🎯 *Our Mission*\n\n"
            "🔹 *Develop People*\n"
            "Provide members with continuous learning, real responsibility, and opportunities to lead.\n\n"
            "🔹 *Create Meaningful Experiences*\n"
            "Deliver valuable experiences that go beyond events and leave a real impact on participants.\n\n"
            "🔹 *Build Professional Partnerships*\n"
            "Create strong, professional relationships that open doors to training, collaboration, and industry opportunities.\n\n"
            "🔹 *Build on a Sustainable System*\n"
            "Improve and develop existing processes, responsibilities, documentation, and knowledge transfer to ensure continuity and accountability.\n\n"
            "🔹 *Empower Innovation & Collaboration*\n"
            "Give every member a voice, encourage new ideas, and connect people to create greater impact together.",
            parse_mode="Markdown"
        )
    elif text == "Our Vision":
        await update.message.reply_photo(
            photo="AgACAgQAAxkBAAIFmmqZ16qj63QcOae7tGU7K0fWZrFiAAI0EWsb467RUPn800hMKH4bAQADAgADeQADPQQ",
            caption=(
                "🔭 *Our Vision — Break The Mold*\n\n"
                "To redefine what a student chapter can be by creating a professional and supportive environment "
                "where every member grows, every voice matters, every partnership creates value, "
                "and every experience leaves a lasting impact."
            ),
            parse_mode="Markdown"
        )
    elif text == "AIChE''s Official Accounts on Social Media":
        links = ("🌐 *Official AIChE Suez Links*\n\n🔗 [Website](https://aichesusc.org/)\n📘 [Facebook](https://www.facebook.com/AIChESUSC)\n💬 [Telegram](https://t.me/AIChESUSC)\n▶️ [YouTube](https://youtube.com/@AIChESUSC1)")
        await update.message.reply_text(links, parse_mode="Markdown", disable_web_page_preview=True)
    elif text == "AIChE''s Mega Events":
        events = [
            (IMAGE_FILE_IDS["PGIE"], "🛢 *PGIE*\nA one-day technical exhibition held annually."),
            (IMAGE_FILE_IDS["AIChE Refining Diploma"], "🎓 *AIChE Refining Diploma*\nAn online 70+ hour diploma."),
            (IMAGE_FILE_IDS["Brain++"], "🧠 *Brain++*\nA two-day mega non-technical event."),
            (IMAGE_FILE_IDS["Career Fair"], "💼 *Visual Intelligence*\nOnline event covering multiple career paths."),
            (IMAGE_FILE_IDS["HYSYS Course"], "💻 *AIChE HYSYS Course*\nAn intensive 4-week in-person training program."),
            (IMAGE_FILE_IDS["Reforming Arena"], "🏆 *AIChE Reforming Arena*\nA 3-week engineering competition for Petroleum Engineering undergraduates across Egypt — featuring 4 technical tracks and a 3-phase challenge."),
            (IMAGE_FILE_IDS["ME Gathering"], "🌍 *AIChE M.E. Gathering Event*\nA 3-week pan-Arab event for Chemical Engineering students from 15+ Arab universities — covering process engineering, simulation, and an NGL optimization challenge judged by industry experts."),
            (IMAGE_FILE_IDS["Panel Discussion"], "🎙️ *AIChE Panel Discussion*\nAn interactive event bridging academia and industry — featuring professors, experts, and graduates in an open dialogue to prepare students for the modern job market."),
        ]
        for file_id, caption in events:
            await update.message.reply_photo(photo=file_id, caption=caption, parse_mode="Markdown")
    elif text == "AIChE''s Main Sponsor":
        await update.message.reply_photo(IMAGE_FILE_IDS["sponsor"], caption="💼 *Our Sponsor*\nBGS Energy Services.", parse_mode="Markdown")
    elif text == "ATB":
        await update.message.reply_document(document="BQACAgQAAxkBAAMjaTam9YikGMM0dYXRPR1eCY6U160AAvYYAAKIRLFR2CJE1_8Eqf42BA")
    elif text == "Capsules":
        await update.message.reply_document(document="BQACAgQAAxkBAAMlaTanQJ7NRWXqmBsqxt8uG3ZK1sUAAvcYAAKIRLFRFYfotpYLFjE2BA")
        await update.message.reply_document(document="BQACAgQAAxkBAAMnaTanijVnKGiX2tTahK-QrE07JdoAAvgYAAKIRLFRIGeummQ3f382BA")
    elif text == "Spark":
        await update.message.reply_text("📚 *Spark Magazine Issues:*\n• [SPARK 9](https://aichesusc.org/articles/15)\n• [SPARK 8](https://aichesusc.org/articles/6)\n• [SPARK 7](https://aichesusc.org/articles/8)", parse_mode="Markdown")
    elif text == "Library":
        await update.message.reply_text("📚 Access our digital library:\n👉 https://drive.google.com/drive/folders/1xjaS-ok3c37gqg5Jq_IbYbOugASO_qCF")
    elif text in ["Level 1", "Level 2", "Level 3", "Level 4"]:
        context.user_data["level"] = text
        if text in ["Level 1", "Level 2"]:
            subs = subjects[text]
            sub_menu = [[s] for s in subs] + [["⬅️ Back", "🏠 Main Menu"]]
            await update.message.reply_text(f"{text} subjects 👇", reply_markup=ReplyKeyboardMarkup(sub_menu, resize_keyboard=True))
        else:
            await update.message.reply_text(f"You selected {text}. Choose a semester 👇", reply_markup=ReplyKeyboardMarkup(semester_menu, resize_keyboard=True))
    elif text in ["Semester 1", "Semester 2"]:
        level = context.user_data.get("level")
        context.user_data["semester"] = text
        key = f"{level} - {text}"
        subs = subjects.get(key, [])
        sub_menu = [[s] for s in subs] + [["⬅️ Back", "🏠 Main Menu"]]
        await update.message.reply_text(f"{key} subjects 👇", reply_markup=ReplyKeyboardMarkup(sub_menu, resize_keyboard=True))
    elif any(text in sublist for sublist in subjects.values()):
        if text in SUBJECT_FILE_IDS and text in SUBJECT_CHANNELS:
            channel_link = SUBJECT_CHANNELS[text]
            safe_link = escape_markdown(channel_link)
            await update.message.reply_text(f"📢 *Join the Telegram Channel for {escape_markdown(text)}:*\n👉 {safe_link}", parse_mode="MarkdownV2", disable_web_page_preview=True)
        else:
            await update.message.reply_text(f"⚠️ Sorry, material for *{text}* not found yet.", parse_mode="Markdown")
    elif text == "⬅️ Back":
        if "semester" in context.user_data:
            context.user_data.pop("semester")
            await update.message.reply_text("Choose a semester 👇", reply_markup=ReplyKeyboardMarkup(semester_menu, resize_keyboard=True))
        elif "level" in context.user_data:
            context.user_data.pop("level")
            await update.message.reply_text("Choose your academic level 👇", reply_markup=ReplyKeyboardMarkup(academic_levels_menu, resize_keyboard=True))
        else:
            await update.message.reply_text("Main menu 👇", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))
    elif text == "🏠 Main Menu":
        context.user_data.clear()
        await update.message.reply_text("Main menu 👇", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))
    else:
        await update.message.reply_text("Please choose an option from the menu below.", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))

# ========= FLASK =========
import threading
flask_app = Flask(__name__)
tls = threading.local()

def get_app():
    if not hasattr(tls, 'app'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tls.loop = loop
        
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(CommandHandler("users", users_count))
        app.add_handler(CommandHandler("myid", myid))
        # Allow media with captions to pass to command handlers if they contain commands
        app.add_handler(MessageHandler((filters.Document.ALL | filters.PHOTO) & ~filters.COMMAND, handle_file))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        tls.app = app
        loop.run_until_complete(app.initialize())
    return tls.app, tls.loop

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    app, loop = get_app()
    update = Update.de_json(data, app.bot)
    loop.run_until_complete(app.process_update(update))
    return "OK", 200

@flask_app.route("/set_webhook")
def set_webhook():
    app, loop = get_app()
    async def do_set():
        await app.bot.set_webhook(url=WEBHOOK_URL)
        info = await app.bot.get_webhook_info()
        return info.url
    url = loop.run_until_complete(do_set())
    return f"✅ Webhook set!<br>URL: {url}"

@flask_app.route("/")
def home():
    return "✅ AIChE Bot is running!"
