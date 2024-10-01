import discord
from discord.ext import commands
import os
import asyncio
from gtts import gTTS
import uuid

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tts_queue = asyncio.Queue()  # Hàng đợi phát TTS
        self.is_playing_tts = False  # Cờ kiểm tra xem có đang phát TTS không
        self.temp_dir = "temp_tts"  # Thư mục chứa các tệp âm thanh tạm thời
        os.makedirs(self.temp_dir, exist_ok=True)

    def replace_special_characters(self, text):
        """Thay thế các ký tự đặc biệt bằng các cụm từ có thể đọc."""
        replacements = {
            ":)": "cười mỉm",
            ":(": "buồn",
            ":D": "cười to",
            ":P": "thè lưỡi",
            "<3": "trái tim",
            ":))": "cười lớn",
            ":o": "ngạc nhiên",
            ":|": "lạnh lùng"
        }
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text

    async def connect_to_voice(self, ctx):
        """Kết nối bot vào voice channel của người dùng hoặc di chuyển bot đến kênh của họ nếu bot đang ở kênh khác."""
        if not ctx.author.voice:
            await ctx.send("Bạn cần ở trong một kênh thoại để sử dụng lệnh này.")
            return False

        voice_client = ctx.voice_client

        if not voice_client:
            await ctx.author.voice.channel.connect()
        elif voice_client.channel != ctx.author.voice.channel:
            await voice_client.move_to(ctx.author.voice.channel)

        return True

    async def play_tts(self, ctx, audio_file):
        """Phát TTS và xử lý âm thanh sau khi phát xong."""
        voice_client = ctx.voice_client

        # Kiểm tra nếu bot đã kết nối voice channel
        if not voice_client or not voice_client.is_connected():
            await ctx.send("Bot chưa kết nối voice channel. Vui lòng thử lại.")
            return

        if voice_client.is_playing():
            await ctx.send("Bot hiện đang phát âm thanh khác. Vui lòng chờ.")
            return

        def after_tts_play(error=None):
            if os.path.exists(audio_file):
                os.remove(audio_file)  # Xóa tệp sau khi phát xong

            self.is_playing_tts = False

            # Kiểm tra xem hàng đợi có yêu cầu phát khác không
            if not self.is_playing_tts and self.tts_queue.empty():
                # Tự động rời khỏi kênh thoại nếu không còn gì để phát
                self.bot.loop.create_task(self.auto_disconnect(ctx))

        try:
            self.is_playing_tts = True
            voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: after_tts_play())
        except Exception as e:
            print(f"Lỗi khi phát TTS: {e}")

    async def play_next_tts(self, ctx):
        """Phát TTS tiếp theo trong hàng đợi."""
        if not self.is_playing_tts and not self.tts_queue.empty():
            ctx, audio_file = await self.tts_queue.get()
            await self.play_tts(ctx, audio_file)

    @commands.command()
    async def wt(self, ctx, *, text):
        """Lệnh để phát TTS văn bản."""
        if not await self.connect_to_voice(ctx):
            return

        # Thay thế các ký tự đặc biệt bằng từ ngữ
        processed_text = self.replace_special_characters(text)

        # Tạo tên tệp duy nhất cho mỗi yêu cầu TTS
        audio_file = os.path.join(self.temp_dir, f"output_{uuid.uuid4()}.mp3")

        try:
            tts = gTTS(processed_text, lang='vi')
            tts.save(audio_file)
        except Exception as e:
            await ctx.send(f"Lỗi khi tạo tệp TTS: {e}")
            return

        await self.tts_queue.put((ctx, audio_file))

        # Chỉ bắt đầu phát nếu bot không đang phát TTS khác
        if not self.is_playing_tts:
            await self.play_next_tts(ctx)

    async def auto_disconnect(self, ctx):
        """Tự động ngắt kết nối bot khỏi voice channel sau khi không còn gì để phát."""
        voice_client = ctx.voice_client
        if voice_client and not self.is_playing_tts and self.tts_queue.empty():
            await voice_client.disconnect()
            await ctx.send("Bot đã rời khỏi kênh thoại.")

    @commands.command(name="ttsleave")
    async def tts_leave(self, ctx):
        """Lệnh để bot rời kênh thoại."""
        voice_client = ctx.voice_client
        if voice_client:
            await voice_client.disconnect()
        else:
            await ctx.send("Bot không ở trong kênh thoại.")

async def setup(bot):
    """Thêm TTS cog vào bot."""
    await bot.add_cog(TTS(bot))
