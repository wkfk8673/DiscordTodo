import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks
import discord
from todo_manager import clear_completed

def get_seconds_until_next_monday(hour=21):
    now = datetime.now()
    days_ahead = (7 - now.weekday()) % 7
    if days_ahead == 0 and now.hour >= hour:
        days_ahead = 7
    next_monday = now + timedelta(days=days_ahead)
    next_monday = next_monday.replace(hour=hour, minute=0, second=0, microsecond=0)
    return (next_monday - now).total_seconds()

def setup_scheduler(bot, channel_id):
    @tasks.loop(seconds=60 * 60 * 24 * 7)
    async def monday_thread_reminder():
        clear_completed()  # :white_check_mark: 완료된 항목 삭제
        channel = bot.get_channel(channel_id)
        if channel:
            thread = await channel.create_thread(
                name=f":pencil: Weekly TODO - {datetime.now().strftime('%Y-%m-%d')}",
                type=discord.ChannelType.public_thread
            )
            await thread.send("@everyone 새로운 한 주입니다! 개인 채널에서 투두리스트 등록 후 아래 스레드에서 [!todo 목록] 을 호출해주세요~ :muscle:")

    @bot.event
    async def on_ready():
        await asyncio.sleep(get_seconds_until_next_monday())
        monday_thread_reminder.start()
