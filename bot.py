import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from todo_manager import (
    add_todo,
    list_todos,
    delete_todo_multiple,
    delete_all_todos,
    mark_done_multiple,
    mark_all_done
)
from scheduler import setup_scheduler
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def todo(ctx, subcommand=None, *args):
    user_id = str(ctx.author.id)
    is_admin = ctx.author.guild_permissions.administrator

    if subcommand == "추가":
        content = " ".join(args)
        if content:
            raw_items = content.replace('\r', '').replace(',', '\n').split('\n')
            items = [item.strip() for item in raw_items if item.strip()]

            for item in items:
                add_todo(user_id, item)

            todos = list_todos(user_id)
            msg = '\n'.join([f"{i+1}. {t['text']}" for i, t in enumerate(todos)])
            await ctx.send(f"✅ `{ctx.author.display_name}` 님의 할 일이 {len(items)}개 추가되었어요.\n\n📋 현재 TODO 목록:\n{msg}")
        else:
            await ctx.send("❗ 추가할 내용을 입력해 주세요.")

    elif subcommand == "목록":
        target_user_id = user_id
        if args and is_admin:
            target_user_id = args[0]
        todos = list_todos(target_user_id)
        if todos:
            msg = '\n'.join([f"{i+1}. {'✅ ' if t.get('done') else ''}{t['text']}" for i, t in enumerate(todos)])
            await ctx.send(f"📋 TODO 목록:\n{msg}")
        else:
            await ctx.send("😴 등록된 할 일이 없어요.")

    elif subcommand == "삭제":
        if not args:
            await ctx.send("❗ 삭제할 번호를 입력해 주세요. (예: `!todo 삭제 1 3`) 또는 `전체`")
            return

        if args[0] == "전체":
            delete_all_todos(user_id)
            await ctx.send("🗑️ 전체 할 일이 삭제되었어요.")
            return

        indexes = [int(i)-1 for i in args if i.isdigit()]
        deleted = delete_todo_multiple(user_id, indexes)
        if deleted:
            msg = '\n'.join([f"- {item}" for item in deleted])
            await ctx.send(f"🗑️ 삭제된 항목:\n{msg}")
        else:
            await ctx.send("❗ 올바른 번호를 입력해 주세요.")

    elif subcommand == "완료":
        if not args:
            await ctx.send("❗ 완료할 번호를 입력해 주세요. (예: `!todo 완료 1 3`) 또는 `전체`")
            return

        if args[0] == "전체":
            mark_all_done(user_id)
            await ctx.send("✅ 전체 항목이 완료 처리되었어요.")
            return

        indexes = [int(i)-1 for i in args if i.isdigit()]
        marked = mark_done_multiple(user_id, indexes)
        if marked:
            msg = '\n'.join([f"- {item}" for item in marked])
            await ctx.send(f"✅ 완료된 항목:\n{msg}")
        else:
            await ctx.send("❗ 올바른 번호를 입력해 주세요.")

    else:
        await ctx.send("❓ 사용법:\n"
                       "`!todo 추가 <내용>` (쉼표/줄바꿈 구분 다중 가능)\n"
                       "`!todo 목록` (관리자는 다른 유저 ID로 조회 가능)\n"
                       "`!todo 삭제 <번호 번호...>` 또는 `전체`\n"
                       "`!todo 완료 <번호 번호...>` 또는 `전체`")

keep_alive()
setup_scheduler(bot, CHANNEL_ID)
bot.run(TOKEN)
