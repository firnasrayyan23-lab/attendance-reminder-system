import os
import re
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.database import (
    add_schedule,
    delete_schedule,
    get_schedules,
    init_db,
)
from src.reminder import DAY_MAP, TIMEZONE, load_all_schedules, register_schedule

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

HELP_TEXT = (
    "📘 MENU ATTENDANCE REMINDER\n\n"
    "/start - Memulai bot\n"
    "/bantuan - Melihat panduan\n"
    "/tambah - Menambahkan jadwal kuliah\n"
    "/jadwal - Melihat daftar jadwal\n"
    "/hapus ID - Menghapus jadwal\n\n"
    "Format tambah jadwal:\n"
    "/tambah Hari | JJ:MM | Mata Kuliah | Ruangan\n\n"
    "Contoh:\n"
    "/tambah Senin | 08:00 | Basis Data | Lab 2\n\n"
    "Pengingat otomatis dikirim 15 menit sebelum kelas."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! 👋\n\n"
        "Selamat datang di Attendance Reminder System.\n"
        "Saya bisa mengingatkan jadwal kuliah dan absensi kamu.\n\n"
        "Ketik /bantuan untuk melihat cara penggunaan."
    )


async def bantuan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Format:\n/tambah Hari | JJ:MM | Mata Kuliah | Ruangan\n\n"
            "Contoh:\n/tambah Senin | 08:00 | Basis Data | Lab 2"
        )
        return

    raw = " ".join(context.args)
    parts = [part.strip() for part in raw.split("|")]
    if len(parts) not in (3, 4):
        await update.message.reply_text(
            "Format belum benar. Gunakan:\n"
            "/tambah Senin | 08:00 | Basis Data | Lab 2"
        )
        return

    day, start_time, course_name = parts[:3]
    room = parts[3] if len(parts) == 4 else ""

    if day.lower() not in DAY_MAP:
        await update.message.reply_text(
            "Nama hari tidak valid. Gunakan Senin, Selasa, Rabu, Kamis, "
            "Jumat, Sabtu, atau Minggu."
        )
        return

    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", start_time):
        await update.message.reply_text("Format jam harus HH:MM, contoh 08:00.")
        return

    chat_id = update.effective_chat.id
    schedule_id = add_schedule(chat_id, course_name, day, start_time, room, 15)
    item = {
        "id": schedule_id,
        "chat_id": chat_id,
        "course_name": course_name,
        "day_of_week": day,
        "start_time": start_time,
        "room": room,
        "reminder_minutes": 15,
    }
    scheduler = context.application.bot_data["scheduler"]
    register_schedule(context.application, scheduler, item)

    await update.message.reply_text(
        "✅ Jadwal berhasil ditambahkan!\n\n"
        f"ID: {schedule_id}\n"
        f"Mata kuliah: {course_name}\n"
        f"Hari: {day.capitalize()}\n"
        f"Mulai: {start_time}\n"
        f"Ruangan: {room or '-'}\n\n"
        "Saya akan mengirim pengingat 15 menit sebelum kelas."
    )


async def jadwal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = get_schedules(update.effective_chat.id)
    if not items:
        await update.message.reply_text(
            "Belum ada jadwal tersimpan.\n"
            "Tambahkan dengan /tambah."
        )
        return

    lines = ["📚 JADWAL KULIAH KAMU\n"]
    for item in items:
        room = f" | {item['room']}" if item["room"] else ""
        lines.append(
            f"ID: {item['id']}\n"
            f"{item['day_of_week'].capitalize()} {item['start_time']} — "
            f"{item['course_name']}{room}\n"
        )
    await update.message.reply_text("\n".join(lines))


async def hapus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Gunakan: /hapus ID\nContoh: /hapus 1")
        return

    schedule_id = int(context.args[0])
    deleted = delete_schedule(schedule_id, update.effective_chat.id)
    if deleted:
        scheduler = context.application.bot_data["scheduler"]
        job_id = f"schedule_{schedule_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        await update.message.reply_text(f"🗑️ Jadwal ID {schedule_id} berhasil dihapus.")
    else:
        await update.message.reply_text("Jadwal tidak ditemukan atau bukan milikmu.")


async def post_init(application: Application):
    init_db()
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.start()
    application.bot_data["scheduler"] = scheduler
    load_all_schedules(application, scheduler)


async def post_shutdown(application: Application):
    scheduler = application.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


def main():
    if not TOKEN or TOKEN == "MASUKKAN_TOKEN_BOT_KAMU_DI_SINI":
        raise SystemExit(
            "Token belum diisi. Masukkan token BotFather ke file .env."
        )

    application = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bantuan", bantuan))
    application.add_handler(CommandHandler("help", bantuan))
    application.add_handler(CommandHandler("tambah", tambah))
    application.add_handler(CommandHandler("jadwal", jadwal))
    application.add_handler(CommandHandler("hapus", hapus))

    print("Attendance Reminder Bot berjalan (zona waktu WITA).")
    application.run_polling()


if __name__ == "__main__":
    main()
