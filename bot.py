import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

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

keep_alive()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def todo(ctx, subcommand=None, *, content=None):
    user_id = str(ctx.author.id)

    if subcommand == '추가':
        if content:
            # 줄바꿈 또는 쉼표(,)로 구분해서 여러 항목 처리
            lines = [line.strip() for line in content.replace('\r', '').split('\n') if line.strip()]
            items = []
            for line in lines:
                items.extend([item.strip() for item in line.split(',') if item.strip()])

            if not items:
                await ctx.send("❗ 추가할 내용을 정확히 입력해 주세요.")
                return

            for item in items:
                add_todo(user_id, item)

            await ctx.send(f"✅ `{ctx.author.display_name}` 님의 할 일 {len(items)}개가 추가되었어요.")
        else:
            await ctx.send("❗ 추가할 내용을 입력해 주세요.")

    elif subcommand == '목록':
        target_user = ctx.author
        if content and ctx.message.mentions:
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("⚠️ 다른 사람의 TODO는 관리자만 볼 수 있어요.")
                return
            target_user = ctx.message.mentions[0]

        user_id = str(target_user.id)
        todos = list_todos(user_id)
        if todos:
            msg = '\n'.join([
                f"{i+1}. {'✅ ' if item['done'] else ''}{item['text']}"
                for i, item in enumerate(todos)
            ])
            await ctx.send(f"📋 `{target_user.display_name}`님의 TODO:\n{msg}")
        else:
            await ctx.send(f"😴 `{target_user.display_name}`님의 할 일이 없어요.")

    elif subcommand == '완료':
        if not content:
            await ctx.send("❗ 완료 처리할 번호를 입력해 주세요.")
            return

        if content.strip() == "전체":
            updated = mark_all_done(user_id)
            if updated:
                await ctx.send(f"✅ 전체 완료 처리됨! ({len(updated)}개)\n" + '\n'.join([f"- {item}" for item in updated]))
            else:
                await ctx.send("😴 완료할 항목이 없어요.")
            return

        try:
            indices = [int(i) - 1 for i in content.split() if i.isdigit()]
            results = mark_done_multiple(user_id, indices)
            if results is None:
                await ctx.send("❗ 완료할 항목을 찾을 수 없어요.")
                return

            msg_lines = []
            for idx, text, newly_done in results:
                if newly_done:
                    msg_lines.append(f"✅ 완료: {idx + 1}. {text}")
                else:
                    msg_lines.append(f"⚠️ 이미 완료됨: {idx + 1}. {text}")
            await ctx.send("\n".join(msg_lines))
        except ValueError:
            await ctx.send("❗ 번호를 정확히 입력해 주세요.")

    elif subcommand == '삭제':
        if not content:
            await ctx.send("❗ 삭제할 번호를 입력해 주세요.")
            return

        if content.strip() == "전체":
            deleted = delete_all_todos(user_id)
            if deleted:
                await ctx.send(f"🗑️ 전체 삭제됨! ({len(deleted)}개)\n" + '\n'.join([f"- {item}" for item in deleted]))
            else:
                await ctx.send("😴 삭제할 항목이 없어요.")
            return

        try:
            indices = [int(i) - 1 for i in content.split() if i.isdigit()]
            deleted = delete_todo_multiple(user_id, indices)
            if deleted:
                msg = '\n'.join([f"🗑️ 삭제됨: {item}" for item in deleted])
                await ctx.send(msg)
            else:
                await ctx.send("❗ 삭제할 항목을 찾을 수 없어요.")
        except ValueError:
            await ctx.send("❗ 번호를 정확히 입력해 주세요.")

    else:
        await ctx.send("❓ 사용법:\n"
                       "`!todo 추가 <내용>` (여러 개 가능)\n"
                       "`!todo 목록` 또는 `!todo 목록 @유저`\n"
                       "`!todo 완료 <번호 ...>` 또는 `!todo 완료 전체`\n"
                       "`!todo 삭제 <번호 ...>` 또는 `!todo 삭제 전체`")

setup_scheduler(bot, CHANNEL_ID)
bot.run(TOKEN)
