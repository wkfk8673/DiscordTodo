import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
import discord

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from todo_manager import save_to_google_sheet, clear_completed, db

def get_gspread_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

def get_seconds_until_next_monday(hour=21):
    now = datetime.now()
    days_ahead = (7 - now.weekday()) % 7
    if days_ahead == 0 and now.hour >= hour:
        days_ahead = 7
    next_monday = now + timedelta(days=days_ahead)
    next_time = next_monday.replace(hour=hour, minute=0, second=0, microsecond=0)
    return (next_time - now).total_seconds()

def setup_scheduler(bot, channel_id):
    @tasks.loop(hours=168)
    async def monday_thread_reminder():
        try:
            client = get_gspread_client()
            sheet = client.open("MyTodoBackup").sheet1
            save_to_google_sheet(sheet)
            all_users = {row["user_id"] for row in db.all()}
            for uid in all_users:
                clear_completed(uid)
        except Exception as e:
            print(f"[백업 오류] {e}")

        channel = bot.get_channel(channel_id)
        if channel:
            thread = await channel.create_thread(
                name=f"📝 Weekly TODO - {datetime.now().strftime('%Y-%m-%d')}",
                type=discord.ChannelType.public_thread
            )
            await thread.send("@everyone 새로운 한 주입니다! 이번 주 TODO를 여기에 적어주세요. 💪")

    @bot.event
    async def on_ready():
        await asyncio.sleep(get_seconds_until_next_monday())
        monday_thread_reminder.start()
