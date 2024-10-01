import discord
from discord.ext import commands
from discord import app_commands
import random

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Hiển thị avatar của người dùng.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        avatar_url = user.display_avatar.url
        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        embed = discord.Embed(title=f"Avatar của {user.name}", color=embed_color)
        embed.set_image(url=avatar_url)
        await interaction.response.send_message(embed=embed)

# Sử dụng async và await
async def setup(bot):
    await bot.add_cog(Avatar(bot))
