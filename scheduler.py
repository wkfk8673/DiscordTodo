import asyncio
from datetime import datetime, timedelta, timezone
from discord.ext import tasks
from todo_manager import clear_completed
from sheets_backup import backup_to_sheets
import discord

KST = timezone(timedelta(hours=9))

def get_seconds_until_next_monday(hour_kst=21):
    now_utc = datetime.now(timezone.utc)
    now_kst = now_utc.astimezone(KST)

    days_ahead = (7 - now_kst.weekday()) % 7
    if days_ahead == 0 and now_kst.hour >= hour_kst:
        days_ahead = 7

    next_monday_kst = (now_kst + timedelta(days=days_ahead)).replace(
        hour=hour_kst, minute=0, second=0, microsecond=0
    )
    next_monday_utc = next_monday_kst.astimezone(timezone.utc)
    return (next_monday_utc - now_utc).total_seconds()

def setup_scheduler(bot, channel_id):
    @tasks.loop(seconds=604800)  # 1주일 간격
    async def monday_reminder():
        backup_to_sheets()  # 자동 백업 실행

        channel = bot.get_channel(channel_id)
        if channel:
            thread = await channel.create_thread(
                name=f"📝 Weekly TODO - {datetime.now(KST).strftime('%Y-%m-%d')}",
                type=discord.ChannelType.public_thread
            )
            await thread.send("@everyone 새로운 한 주입니다! 아래 스레드에 이번 주 TODO를 적어주세요. 💪")

            # 모든 멤버별 완료된 항목 삭제
            for member in channel.members:
                clear_completed(str(member.id))

    @bot.event
    async def on_ready():
        await asyncio.sleep(get_seconds_until_next_monday())
        monday_reminder.start()
