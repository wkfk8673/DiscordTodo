import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from todo_manager import *
from scheduler import setup_scheduler
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def todo(ctx, sub=None, *args):
    user_id = str(ctx.author.id)

    if sub == "추가":
        content = " ".join(args)
        if content:
            add_todo(user_id, content)
            await ctx.send(f"✅ `{ctx.author.display_name}` 님의 할 일이 추가되었어요.")
        else:
            await ctx.send("❗ 추가할 내용을 입력해 주세요.")

    elif sub == "목록":
        todos = list_todos(user_id)
        if todos:
            msg = '\n'.join([f"{i+1}. {'✅' if t['done'] else '⬜'} {t['text']}" for i, t in enumerate(todos)])
            await ctx.send(f"📋 `{ctx.author.display_name}`님의 TODO:\n{msg}")
        else:
            await ctx.send("😴 등록된 할 일이 없어요.")

    elif sub == "삭제":
        if len(args) == 1 and args[0] == "전체":
            delete_all_todos(user_id)
            await ctx.send("🗑️ 전체 할 일이 삭제되었습니다.")
        else:
            indexes = [int(i) - 1 for i in args if i.isdigit()]
            deleted = delete_todo_multiple(user_id, indexes)
            await ctx.send(f"🗑️ 삭제됨: {', '.join(deleted)}") if deleted else await ctx.send("❗ 삭제할 번호를 확인해주세요.")

    elif sub == "완료":
        if len(args) == 1 and args[0] == "전체":
            mark_all_done(user_id)
            await ctx.send("✅ 모든 항목이 완료 처리되었습니다.")
        else:
            indexes = [int(i) - 1 for i in args if i.isdigit()]
            done = mark_done_multiple(user_id, indexes)
            await ctx.send(f"✅ 완료됨: {', '.join(done)}") if done else await ctx.send("❗ 완료할 번호를 확인해주세요.")

    else:
        await ctx.send("❓ 사용법: `!todo 추가`, `!todo 목록`, `!todo 삭제`, `!todo 완료`")

keep_alive()
setup_scheduler(bot, CHANNEL_ID)
bot.run(TOKEN)
