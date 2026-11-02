from datetime import time
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.database import get_schedules

TIMEZONE = ZoneInfo("Asia/Makassar")  # WITA
DAY_MAP = {
    "senin": "mon",
    "selasa": "tue",
    "rabu": "wed",
    "kamis": "thu",
    "jumat": "fri",
    "sabtu": "sat",
    "minggu": "sun",
}


def reminder_clock(start_time, minutes_before):
    hour, minute = map(int, start_time.split(":"))
    total = hour * 60 + minute - minutes_before
    total %= 24 * 60
    return total // 60, total % 60


def register_schedule(application, scheduler, item):
    day = DAY_MAP[item["day_of_week"].lower()]
    hour, minute = reminder_clock(item["start_time"], item["reminder_minutes"])

    async def send_reminder():
        room_text = f"\nRuangan: {item['room']}" if item["room"] else ""
        message = (
            "PENGINGAT ABSENSI KULIAH\n\n"
            f"Mata kuliah: {item['course_name']}\n"
            f"Hari: {item['day_of_week'].capitalize()}\n"
            f"Mulai: {item['start_time']}"
            f"{room_text}\n\n"
            f"Jangan lupa melakukan presensi. Pengingat ini dikirim "
            f"{item['reminder_minutes']} menit sebelum kelas dimulai."
        )
        await application.bot.send_message(chat_id=item["chat_id"], text=message)

    scheduler.add_job(
        send_reminder,
        trigger=CronTrigger(day_of_week=day, hour=hour, minute=minute, timezone=TIMEZONE),
        id=f"schedule_{item['id']}",
        replace_existing=True,
        misfire_grace_time=3600,
    )


def load_all_schedules(application, scheduler):
    for item in get_schedules():
        register_schedule(application, scheduler, item)
