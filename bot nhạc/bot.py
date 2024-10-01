import os
import discord
import asyncio
import logging
from discord.ext import commands
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

# Thiết lập logging
logging.basicConfig(level=logging.INFO)

# Cấu hình intents cho bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  # Đảm bảo bot có quyền truy cập guild (cần cho slash commands)
intents.members = True  # Đảm bảo bot có thể quản lý thành viên (mute, ban)

# Khởi tạo bot với prefix "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Danh sách các module (cogs) cần load
initial_extensions = ['cogs.music', 'cogs.moderation', 'cogs.avatar', 'cogs.tts']

# Hàm load các cogs
async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)  # Sử dụng await vì load_extension là coroutine
            logging.info(f"Loaded extension: {extension}")
        except Exception as e:
            logging.error(f"Failed to load extension {extension}: {e}")

# Đồng bộ lệnh slash khi bot khởi động
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()  # Đồng bộ lệnh slash với Discord
        logging.info(f'Logged in as {bot.user} - Lệnh đã đồng bộ thành công.')
    except discord.HTTPException as e:
        logging.error(f'Lỗi khi đồng bộ lệnh: {e}')

# Hàm chính để load cogs và khởi chạy bot
async def main():
    await load_extensions()
    
    # Lấy token từ biến môi trường
    bot_token = os.getenv('DISCORD_BOT_TOKEN')

    if not bot_token:
        logging.error("Bot token không được tìm thấy trong biến môi trường.")
    else:
        try:
            await bot.start(bot_token)
        except discord.LoginFailure:
            logging.error("Token không hợp lệ, vui lòng kiểm tra lại.")
        except discord.HTTPException as e:
            logging.error(f'Lỗi kết nối tới Discord API: {e}')

# Chạy bot
if __name__ == '__main__':
    asyncio.run(main())  # Sử dụng asyncio.run để chạy bot
