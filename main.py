import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request

# ========= BOT TOKEN =========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in environment variables!")

# ⚠️ غيّر ده لاسم حسابك على PythonAnywhere
PYTHONANYWHERE_USERNAME = os.environ.get("PA_USERNAME", "AmirEhab")
WEBHOOK_URL = f"https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com/{BOT_TOKEN}"

# ========= LOGGING =========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========= MENUS =========
main_menu = [
    ["Know AIChE"],
    ["AIChE Technical Products"],
    ["Academic"]
]

know_aiche_menu = [
    ["Who Are We?"],
    ["Our Vision", "Our Mission"],
    ["AIChE''s Official Accounts on Social Media"],
    ["AIChE''s Mega Events"],
    ["AIChE''s Main Sponsor"],
    ["⬅️ Back", "🏠 Main Menu"]
]

tech_products_menu = [
    ["ATB", "Spark"],
    ["Capsules", "Library"],
    ["⬅️ Back", "🏠 Main Menu"]
]

academic_levels_menu = [
    ["Level 1", "Level 2"],
    ["Level 3", "Level 4"],
    ["⬅️ Back", "🏠 Main Menu"]
]

semester_menu = [
    ["Semester 1"],
    ["Semester 2"],
    ["⬅️ Back", "🏠 Main Menu"]
]

# ========= SUBJECTS =========
subjects = {
    "Level 1": [
        "Introduction to Petroleum Refining",
        "Fundamentals of Chemical Engineering",
        "Organic Chemistry"
    ],
    "Level 2": [
        "Petroleum Refining Engineering 1",
        "Crude Oil Evaluation",
        "Unit Operation 1",
        "Water Treatment"
    ],
    "Level 3 - Semester 1": [
        "Unit Operation 2",
        "Reactions",
        "Corrosion",
        "Introduction to Petroleum Engineering",
        "Petrochemicals 1"
    ],
    "Level 3 - Semester 2": [
        "Computer Applications",
        "Heat Transfer",
        "Petroleum Products Testing",
        "HYSYS",
        "Storage and Transportation",
        "Unit Processes"
    ],
    "Level 4 - Semester 1": [
        "Plant Design",
        "Pollution Control",
        "Design of Refining Equipment",
        "Process Control",
        "Petroleum Refining 2",
        "Operation Research in Chemical Engineering"
    ],
    "Level 4 - Semester 2": [
        "Furnace Design",
        "Petrochemicals 2",
        "Process Design",
        "Gas Engineering"
    ]
}

# ========= FILE IDs =========
FILE_IDS = {
    "ATB":
    "BQACAgQAAxkBAAIE-Gj637FZYbH9U7T-f0OHIPNiXAzpAALuGgACBh_QUwL8sLv4-9xcNgQ",
    "Spark":
    "BQACAgQAAxkBAAIE9Gj635nr9GNSf3xRYEDSagiRaUPXAALsGgACBh_QUzSxIPI3iPu0NgQ",
    "Capsules":
    "BQACAgQAAxkBAAIE9mj636WqFwvFpRekAqlDVxS_lLpVAALtGgACBh_QU-O-68UQ_XKpNgQ"
}

SUBJECT_FILE_IDS = {
    "Introduction to Petroleum Refining":
    "BQACAgQAAxkBAAIDyWj6LZsAAe2QrQTY_z2R6rWTNCgwyAACuBsAArWs0VOP-RJ2LEIkazYE",
    "Fundamentals of Chemical Engineering":
    "BQACAgQAAxkBAAIDy2j6LzphWLCUV16D8CCyVw-4w5d7AAK6GwACtazRU9mz3a_ClI3pNgQ",
    "Organic Chemistry":
    "BQACAgQAAxkBAAIDzWj6MN3TgCodHYtFsLuEWcaazxEwAAK9GwACtazRUzl_L47oaJ9BNgQ",
    "Petroleum Refining Engineering 1":
    "BQACAgQAAxkBAAID0Wj6OWeqjdZdepJur5gVtVG_Om66AALUGwACtazRU0FrkAxKoOonNgQ",
    "Crude Oil Evaluation":
    "BQACAgQAAxkBAAID1Wj6RdsK8q3mc8TuPjNnPfHgoJQEAAJjGwACtazZU2jidsW-aBnRNgQ",
    "Unit Operation 1":
    "BQACAgQAAxkBAAID02j6OcE4SnIW1luTGO0_XytuzvhBAALZGwACtazRU2ziCFv8B9_XNgQ",
    "Water Treatment":
    "BQACAgQAAxkBAAIDz2j6MgI0y-DngmZIn8U7kmV9uo-rAAK-GwACtazRU8oLdizZJY7tNgQ",
    "Unit Operation 2":
    "BQACAgQAAxkBAAID22j6Vw02RCHVpAeCmsKAiBJzEMWlAALyGwACtazZU9FgKQ2_bbwiNgQ",
    "Reactions":
    "BQACAgQAAxkBAAID42j6aV-XiuGb_TeqmWOaX4bAJb2AAAK_HAACtazZUxqVwmKY6yuANgQ",
    "Corrosion":
    "BQACAgQAAxkBAAID2Wj6VB0YvBFK-KOgcTBbSXiLjsCaAAKZGwACtazZU-u4MOC0BthwNgQ",
    "Introduction to Petroleum Engineering":
    "BQACAgQAAxkBAAID4Wj6ZB9UjgABO9nfXD32GEJ8X9wMhgACoRwAArWs2VN0JR-TqlYZ3TYE",
    "Petrochemicals 1":
    "BQACAgQAAxkBAAID12j6UISYOEM-Y3yrPBBhmvIDhnOcAAJ7GwACtazZUz3sciWfXBFqNgQ",
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
    "Unit Operation 2": "https://t.me/+q4AZdDWhAJRmOTA8",
    "Reactions": "https://t.me/+dJvCgTIop0xkNDQ0",
    "Corrosion": "https://t.me/+3jn8XIFkZh1jOGU0",
    "Introduction to Petroleum Engineering": "https://t.me/+TMcsxTSAE1llOGJk",
    "Petrochemicals 1": "https://t.me/+sv9Ss56Jb6ozZWU0",
    "Pollution Control": "https://t.me/+_anxt75rM-9hZDg0",
    "Process Control": "https://t.me/+W3gF_ZzYplRjZTk0",
    "Operation Research in Chemical Engineering": "https://t.me/+NkrqGY1_zpBlZWI8",
    "Storage and Transportation": "https://t.me/+xRbObas2ZasyNThk",
    "HYSYS": "https://t.me/+EaF8J_jSaoMxMzc0",
    "Computer Applications": "https://t.me/+2tUm36T2__dkMDg0",
    "Heat Transfer": "https://t.me/+OgQyvv7MAIxjYmE0",
    "Design of Refining Equipment": "https://t.me/+8qqZ9VjdvIJhYmQ0",
    "Plant Design": "https://t.me/+g2kuiiTgu6YzZDNk",
    "Unit Processes": "https://t.me/+Vph_onDDnbkzODk0",
    "Petroleum Products Testing": "https://t.me/+SqG_MwHV41RiYTlk",
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
    "Brain++": "AgACAgQAAxkBAANAaTapr2Y3ZvGgyX7_6WOniItU7M8AAvMLaxuIRLFRkg9aGyLAtJQBAAMCAAN5AAM2BA",
    "sponsor": "AgACAgQAAxkBAANMaTarVTZt0lSfdnHziXmFVe05Tm0AAvkLaxuIRLFRC7g3mpsf9bEBAAMCAAN5AAM2BA",
}

# ========= FLASK APP =========
flask_app = Flask(__name__)

# ========= BOT APPLICATION =========
bot_app = Application.builder().token(BOT_TOKEN).build()

# ========= HELPERS =========
def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text

# ========= HANDLERS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to AIChE Suez Chapter Bot! 👋\nPlease choose an option below:",
        reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"🖼️ Image file_id:\n{file_id}")
    elif update.message.document:
        file_id = update.message.document.file_id
        await update.message.reply_text(f"📄 Document file_id:\n{file_id}")
    else:
        await update.message.reply_text("⚠️ Unsupported file type.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Know AIChE":
        await update.message.reply_text("Learn more about AIChE 👇", reply_markup=ReplyKeyboardMarkup(know_aiche_menu, resize_keyboard=True))
    elif text == "AIChE Technical Products":
        await update.message.reply_text("Explore AIChE Technical Products 👇", reply_markup=ReplyKeyboardMarkup(tech_products_menu, resize_keyboard=True))
    elif text == "Academic":
        await update.message.reply_text("Choose your academic level 👇", reply_markup=ReplyKeyboardMarkup(academic_levels_menu, resize_keyboard=True))
    elif text == "Who Are We?":
        await update.message.reply_photo(IMAGE_FILE_IDS["who_we_are"], caption="🌐 *Who We Are*\nAIChE stands for 'American Institute of Chemical Engineers'. It is the world's leading organization for chemical engineering professionals.", parse_mode="Markdown")
    elif text == "Our Mission":
        await update.message.reply_text("🎯 *Our Mission*\nTo empower students with technical knowledge, leadership skills, and industrial exposure.", parse_mode="Markdown")
    elif text == "Our Vision":
        await update.message.reply_photo(IMAGE_FILE_IDS["our_vision"], caption="🚀 *Reforming Spark*\nEvery Evolution Starts with a Spark.", parse_mode="Markdown")
    elif text == "AIChE''s Official Accounts on Social Media":
        links = ("🌐 *Official AIChE Suez Links*\n\n"
                 "🔗 Website: [aichesusc.org](https://aichesusc.org/)\n"
                 "📘 Facebook: [AIChE Suez](https://www.facebook.com/AIChESUSC)\n"
                 "💼 LinkedIn: [AIChE Suez Student Chapter](https://www.linkedin.com/company/aichesuez/)\n"
                 "📸 Instagram: [@aichesusc](https://instagram.com/aichesusc)\n"
                 "💬 Telegram: [AIChE Suez Channel](https://t.me/AIChESUSC)\n"
                 "▶️ YouTube: [AIChE Suez Channel](https://youtube.com/@AIChESUSC1)")
        await update.message.reply_text(links, parse_mode="Markdown", disable_web_page_preview=True)
    elif text == "AIChE''s Mega Events":
        events = [
            (IMAGE_FILE_IDS["PGIE"], "🛢 *PGIE*\nA one-day technical exhibition and conference held annually."),
            (IMAGE_FILE_IDS["AIChE Refining Diploma"], "🎓 *AIChE Refining Diploma*\nAn online 70+ hour diploma."),
            (IMAGE_FILE_IDS["Brain++"], "🧠 *Brain++*\nA two-day mega non-technical event."),
            (IMAGE_FILE_IDS["Career Fair"], "💼 *Visual Intelligence*\nAn online event covering multiple career paths."),
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
        spark_links = ("📚 *Spark Magazine Issues:*\n"
                       "• [SPARK Magazine 9](https://aichesusc.org/articles/15)\n"
                       "• [SPARK Magazine 8](https://aichesusc.org/articles/6)\n"
                       "• [SPARK Magazine 7](https://aichesusc.org/articles/8)\n"
                       "• [SPARK Magazine 6](https://aichesusc.org/articles/1)")
        await update.message.reply_text(spark_links, parse_mode="Markdown")
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
        if text in SUBJECT_FILE_IDS:
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
        await update.message.reply_text("Please choose an option from the menu below.")

# ========= REGISTER HANDLERS =========
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
bot_app.add_handler(MessageHandler(filters.TEXT, handle_message))

# ========= WEBHOOK ROUTE =========
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    import json
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    await bot_app.initialize()
    await bot_app.process_update(update)
    return "OK", 200

@flask_app.route("/")
def home():
    return "AIChE Suez Chapter Bot is running! ✅"

# ========= SET WEBHOOK ROUTE =========
@flask_app.route("/set_webhook")
async def set_webhook():
    await bot_app.bot.set_webhook(url=WEBHOOK_URL)
    return f"Webhook set to: {WEBHOOK_URL}"
