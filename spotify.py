
# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025
import asyncio
import logging
import os
import re
import shutil
import uuid
import json
from pathlib import Path

from dotenv import dotenv_values

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
DOWNLOADS_DIR = BASE_DIR / "downloads"

SPOTIFY_URL_RE = re.compile(
    r"(https?://open\.spotify\.com/(?:intl-\w+/)?(?:track|album|playlist|artist)/\w+"
    r"|spotify:(?:track|album|playlist|artist):\w+)",
    re.IGNORECASE,
)

FOUND_RE = re.compile(r"Found (\d+) song", re.IGNORECASE)
COMPLETE_RE = re.compile(r"(\d+)/(\d+) complete")

STAGE_RE = re.compile(
    r"^(?P<name>.+): (?P<stage>Searching for song|Getting audio meta|Downloading|"
    r"Converting|Embedding metadata|Done|Skipped|Error)$"
)

STAGE_FRACTION = {
    "Searching for song": 0.15,
    "Getting audio meta": 0.35,
    "Downloading": 0.55,
    "Converting": 0.75,
    "Embedding metadata": 0.90,
    "Done": 1.0,
    "Skipped": 1.0,
    "Error": 1.0,
}

STAGE_LABEL = {
    "Searching for song": " جارٍ البحث",
    "Getting audio meta": "جارٍ جلب البيانات الوصفية",
    "Downloading": " جارٍ تحميل الصوت",
    "Converting": " جارٍ التحويل",
    "Embedding metadata": " جارٍ إضافة الوسوم",
    "Done": " تم",
    "Skipped": "تم التحميل مسبقاً",
    "Error": " خطأ",
}


# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"AUTH": {"ENABLE": False, "PASSWORD": "", "OWNER_ID": None, "USERS": []}}


def save_config(config: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


config = load_config()
config.setdefault("AUTH", {})
config["AUTH"].setdefault("ENABLE", False)
config["AUTH"].setdefault("PASSWORD", "")
config["AUTH"].setdefault("OWNER_ID", None)
config["AUTH"].setdefault("USERS", [])


def get_token() -> str:
    env = dotenv_values(BASE_DIR / ".env")
    token = env.get("TELEGRAM_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError(
            "لم يتم العثور على رمز تيليجرام. ضع TELEGRAM_TOKEN في ملف .env "
            "أو اضبطه كمتغير بيئة."
        )
    return token


def is_authorized(chat_id: int) -> bool:
    if not config["AUTH"]["ENABLE"]:
        return True
    if config["AUTH"]["OWNER_ID"] and chat_id == config["AUTH"]["OWNER_ID"]:
        return True
    return chat_id in config["AUTH"]["USERS"]


def try_login(chat_id: int, text: str) -> bool:
    password = config["AUTH"]["PASSWORD"]
    if password and text.strip() == password:
        if chat_id not in config["AUTH"]["USERS"]:
            config["AUTH"]["USERS"].append(chat_id)
        if not config["AUTH"]["OWNER_ID"]:
            config["AUTH"]["OWNER_ID"] = chat_id
        save_config(config)
        return True
    return False


def render_progress(state: dict, width: int = 20) -> str:
    total = state["total"] or 1
    completed = state["completed"]
    stage = state["stage"]
    frac = STAGE_FRACTION.get(stage, 0.0)
    current = completed + (0.0 if stage in ("Done", "Skipped", "Error") else frac)
    overall = min(current / total, 1.0)

    filled = int(width * overall)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(overall * 100)

    lines = []
    if total > 1:
        lines.append(f" جارٍ التحميل  ({min(completed + 1, total)}/{total})")
    else:
        lines.append(" جارٍ التحميل")
    if state["name"]:
        lines.append(f"🎵 {state['name']}")
    lines.append(STAGE_LABEL.get(stage, "…"))
    lines.append(f"[{bar}] {pct}%")
    return "\n".join(lines)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if config["AUTH"]["ENABLE"] and not is_authorized(chat_id):
        await update.message.reply_text(
            " أهلاً بك!\n\nهذا البوت خاص. يرجى إرسال كلمة المرور لتسجيل الدخول. "
            "إذا كنت لا تعرفها، تواصل مع مالك البوت."
        )
        return
    await update.message.reply_text(
        "🎵 *بوت تحميل سبوتيفاي*\n\n"
        "أرسل لي رابط سبوتيفاي وسأجلب لك الصوت.\n\n"
        "الروابط المدعومة:\n"
        "• مقطع\n• ألبوم\n• قائمة تشغيل\n• فنان\n\n"
        "مثال: `https://open.spotify.com/track/...`",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "فقط أرسل رابط سبوتيفاي (مقطع، ألبوم، قائمة تشغيل أو فنان) وسأقوم "
        "بتحميله وإرسال ملفات MP3 لك.\n\n"
        "الأوامر:\n"
        "/start – الترحيب / تسجيل الدخول\n"
        "/help – هذه الرسالة\n"
        "/logout – تسجيل الخروج (إذا كانت المصادقة مفعّلة)"
    )


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in config["AUTH"]["USERS"]:
        config["AUTH"]["USERS"].remove(chat_id)
        save_config(config)
        await update.message.reply_text(" تم تسجيل خروجك.")
    else:
        await update.message.reply_text("لم تكن مسجلاً للدخول.")


async def run_spotdl(url: str, out_dir: Path, progress_cb) -> None:
    output_template = str(out_dir / "{artists} - {title}.{output-ext}")
    cmd = [
        "spotdl",
        "download",
        url,
        "--simple-tui",
        "--output",
        output_template,
    ]
    logger.info("جارٍ التشغيل: %s", " ".join(cmd))

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    state = {"total": 0, "completed": 0, "name": "", "stage": ""}
    assert process.stdout is not None
    async for raw in process.stdout:
        line = raw.decode(errors="ignore").strip()
        if not line:
            continue
        logger.info("[spotdl] %s", line)

        found = FOUND_RE.search(line)
        if found:
            state["total"] = int(found.group(1))
            await progress_cb(state)
            continue

        complete = COMPLETE_RE.search(line)
        if complete:
            state["completed"] = int(complete.group(1))
            state["total"] = max(state["total"], int(complete.group(2)))
            await progress_cb(state)
            continue

        stage_match = STAGE_RE.match(line)
        if stage_match:
            state["name"] = stage_match.group("name")
            state["stage"] = stage_match.group("stage")
            if state["stage"] not in ("Done", "Skipped"):
                await progress_cb(state)

    await process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"خرج spotdl بالرمز {process.returncode}")


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat_id = update.effective_chat.id
    text = message.text or ""

    match = SPOTIFY_URL_RE.search(text)

    if config["AUTH"]["ENABLE"] and not is_authorized(chat_id):
        if try_login(chat_id, text):
            await message.reply_text(" تم تسجيل الدخول بنجاح. استمتع! ")
        else:
            await message.reply_text(
                " هذا البوت خاص وأنت غير مسجل للدخول.\n"
                "يرجى إرسال كلمة المرور لتسجيل الدخول."
            )
        return

    if not match:
        await message.reply_text(
            "يرجى إرسال رابط سبوتيفاي صحيح (مقطع، ألبوم، قائمة تشغيل أو فنان)."
        )
        return

    url = match.group(1)
    request_id = uuid.uuid4().hex[:12]
    out_dir = DOWNLOADS_DIR / request_id
    out_dir.mkdir(parents=True, exist_ok=True)

    status = await message.reply_text(" جارٍ الجلب…")

    last_edit = {"text": ""}

    async def progress_cb(state: dict) -> None:
        text = render_progress(state)
        if text == last_edit["text"]:
            return
        last_edit["text"] = text
        try:
            await status.edit_text(text)
        except Exception:
            pass

    try:
        await context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        await run_spotdl(url, out_dir, progress_cb)
    except FileNotFoundError:
        await status.edit_text(
            " spotdl غير مثبت على الخادم. شغّل `pip install spotdl`."
        )
        shutil.rmtree(out_dir, ignore_errors=True)
        return
    except Exception as exc: 
        logger.exception("فشل التحميل")
        await status.edit_text(f" فشل التحميل: {exc}")
        shutil.rmtree(out_dir, ignore_errors=True)
        return

    mp3_files = sorted(out_dir.rglob("*.mp3"))
    if not mp3_files:
        await status.edit_text(
            " لم أتمكن من العثور على الأغنية أو تحميلها. قد تكون غير متاحة."
        )
        shutil.rmtree(out_dir, ignore_errors=True)
        return

    await status.edit_text(f" جارٍ إرسال {len(mp3_files)} مقطع…")
    sent = 0
    for mp3 in mp3_files:
        title = mp3.stem
        performer = None
        if " - " in title:
            performer, title = title.split(" - ", 1)
        try:
            await context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_VOICE)
            with open(mp3, "rb") as audio:
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=audio,
                    title=title,
                    performer=performer,
                    read_timeout=1000,
                    write_timeout=1000,
                )
            sent += 1
        except Exception: 
            logger.exception("فشل إرسال %s", mp3)

    shutil.rmtree(out_dir, ignore_errors=True)

    if sent:
        await status.edit_text(f" تم! أُرسل {sent} مقطع. استمتع ")
    else:
        await status.edit_text(" حدثت مشكلة أثناء إرسال الصوت.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("تسبب التحديث في خطأ", exc_info=context.error)


def main() -> None:
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    token = get_token()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_error_handler(on_error)

    logger.info("بدأ البوت…")
    app.run_polling()

# الترخيص: @TopVeGa
# العلامة التجارية: VEGA & Logic
# حقوق الطبع والنشر: © 2015 - 2025

if __name__ == "__main__":
    main()