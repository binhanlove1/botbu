import discord
from discord.ext import commands
import yt_dlp
import asyncio

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': 'True'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Hàng đợi bài hát
        self.current_requester = None  # Lưu ID của người yêu cầu bài hát hiện tại

    @commands.command()
    async def witch(self, ctx, *, query_or_url):
        voice_client = ctx.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                voice_client = ctx.voice_client
            else:
                await ctx.send("Bạn cần tham gia một kênh thoại trước!")
                return

        if query_or_url.startswith("http://") or query_or_url.startswith("https://"):
            youtube_url = query_or_url
        else:
            youtube_url = await search_youtube(query_or_url)

        if youtube_url:
            self.queue.append((ctx.author.id, youtube_url))  # Lưu cả ID người yêu cầu
            await ctx.send(f"Đã thêm vào hàng đợi: {youtube_url}")
            if not voice_client.is_playing() and not voice_client.is_paused():
                await self.play_next(ctx)
        else:
            await ctx.send("Không tìm thấy bài hát.")

    async def play_next(self, ctx):
        voice_client = ctx.guild.voice_client
        if not voice_client.is_playing():
            if self.queue:
                requester_id, youtube_url = self.queue.pop(0)
                self.current_requester = requester_id  # Lưu ID của người yêu cầu bài hát hiện tại
                audio_source = await get_audio_source(youtube_url)
                voice_client.play(audio_source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            else:
                await ctx.send("Hàng đợi đã hết bài.")
                await voice_client.disconnect()

    @commands.command()
    async def witchskip(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client.is_playing():
            # Chỉ người yêu cầu bài hát hiện tại mới có thể skip
            if self.current_requester == ctx.author.id:
                voice_client.stop()
                await self.play_next(ctx)
            else:
                await ctx.send("Bạn không có quyền bỏ qua bài hát này.")
        else:
            await ctx.send("Hiện không có bài hát nào đang phát.")

    @commands.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            # Chỉ người yêu cầu bài hát hiện tại mới có thể stop
            if self.current_requester == ctx.author.id:
                voice_client.stop()  # Dừng bài hát hiện tại và phát bài kế tiếp
                await self.play_next(ctx)  # Không xóa hàng đợi mà tiếp tục phát bài kế tiếp
                await ctx.send("Đã dừng bài hát hiện tại và phát bài tiếp theo trong hàng đợi.")
            else:
                await ctx.send("dừng cái cc nè .")
        else:
            await ctx.send("Không có nhạc đang phát.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Bot đã rời kênh thoại.")
        else:
            await ctx.send("Bot không có trong kênh thoại nào.")

    @commands.command()
    async def witchlist(self, ctx):
        """Lệnh này sẽ hiển thị danh sách các bài hát trong hàng đợi."""
        if self.queue:
            queue_list = "\n".join([f"{index + 1}. {url}" for index, (_, url) in enumerate(self.queue)])
            await ctx.send(f"**Danh sách hàng đợi:**\n{queue_list}")
        else:
            await ctx.send("Hàng đợi hiện đang trống.")

async def get_audio_source(url):
    info = ytdl.extract_info(url, download=False)
    audio_url = info['url']
    return discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)

async def search_youtube(query):
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        return info['webpage_url']
    except Exception as e:
        return None

async def setup(bot):
    await bot.add_cog(Music(bot))
