import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
import discord
from todo_manager import clear_completed

def get_seconds_until_next_monday(hour=21):
    now = datetime.now()
    next_monday = now + timedelta(days=(7 - now.weekday()) % 7)
    next_monday = next_monday.replace(hour=hour, minute=0, second=0, microsecond=0)
    # 만약 시간이 이미 지났으면 다음주로 설정
    if next_monday <= now:
        next_monday += timedelta(days=7)
    return (next_monday - now).total_seconds()

def setup_scheduler(bot, channel_id):
    @tasks.loop(hours=168)  # 7일 = 168시간
    async def monday_thread_reminder():
        channel = bot.get_channel(channel_id)
        if channel:
            thread = await channel.create_thread(
                name=f"📝 Weekly TODO - {datetime.now().strftime('%Y-%m-%d')}",
                type=discord.ChannelType.public_thread
            )
            await thread.send("@everyone 새로운 한 주입니다! 아래 스레드에 이번 주 TODO를 적어주세요. 💪")
            # 완료된 항목 삭제
            for user_id in [doc['user_id'] for doc in bot.todo_db.all()]:
                clear_completed(user_id)

    @bot.event
    async def on_ready():
        await asyncio.sleep(get_seconds_until_next_monday())
        monday_thread_reminder.start()
