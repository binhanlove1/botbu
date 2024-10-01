import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_roles(required_roles):
        """Decorator kiểm tra xem người dùng có vai trò yêu cầu hay không."""
        async def predicate(interaction: discord.Interaction) -> bool:
            member_roles = [role.name for role in interaction.user.roles]
            # Kiểm tra nếu người dùng có ít nhất một vai trò yêu cầu
            if not any(role in member_roles for role in required_roles):
                # Gửi thông báo nếu không có vai trò phù hợp
                await interaction.response.send_message(
                    f"Bạn không có quyền sử dụng lệnh này. Yêu cầu các vai trò: {', '.join(required_roles)}", 
                    ephemeral=True  # Vẫn giữ ephemeral để thông báo cho người dùng không đủ quyền chỉ thấy tin nhắn
                )
                return False
            return True
        return app_commands.check(predicate)

    @app_commands.command(name="mute", description="Mute một thành viên trong một khoảng thời gian nhất định (tính theo phút).")
    @has_roles(["Trưởng lão", "Witch Support"])  # Chỉ những người có vai trò Trưởng lão hoặc Witch Support được phép sử dụng
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Không có lý do cụ thể"):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            # Tạo role Muted và cài đặt quyền cho nó
            muted_role = await interaction.guild.create_role(name="Muted", reason="Tạo role Muted tự động")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        
        await member.add_roles(muted_role)

        # Gửi tin nhắn công khai cho tất cả mọi người trong kênh
        await interaction.response.send_message(f"{member.mention} đã bị mute trong {minutes} phút. Lý do: {reason}.")
        
        # Gửi tin nhắn riêng cho thành viên bị mute
        try:
            await member.send(f"Bạn đã bị mute trong {minutes} phút tại server {interaction.guild.name}. Lý do: {reason}.")
        except discord.Forbidden:
            await interaction.followup.send(f"Không thể gửi tin nhắn cho {member.mention}.")

        # Chờ khoảng thời gian chỉ định trước khi unmute
        await asyncio.sleep(minutes * 60)
        await member.remove_roles(muted_role)
        await interaction.followup.send(f"{member.mention} đã được unmute sau {minutes} phút.")

    @app_commands.command(name="unmute", description="Unmute một thành viên.")
    @has_roles(["Admin", "Moderator"])  # Chỉ những người có vai trò Admin hoặc Moderator được phép sử dụng
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(f"{member.mention} đã được unmute.")
        else:
            await interaction.response.send_message(f"{member.mention} không bị mute.")

    @app_commands.command(name="ban", description="Ban một thành viên khỏi server.")
    @has_roles(["Admin"])  # Chỉ những người có vai trò Admin được phép sử dụng
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do cụ thể"):
        try:
            await interaction.guild.ban(member, reason=reason)
            await interaction.response.send_message(f"{member.mention} đã bị ban vì lý do: {reason}.")
        except discord.Forbidden:
            await interaction.response.send_message("Bot không có quyền ban thành viên này.")
        except Exception as e:
            await interaction.response.send_message(f"Có lỗi xảy ra: {e}")

# Sử dụng async và await trong setup
async def setup(bot):
    await bot.add_cog(Moderation(bot))
