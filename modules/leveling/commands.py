import os

import discord
from discord import commands
from discord.ext import commands as ext_commands
from ORM import Level
from managers import settings_manager, SettingsManager
from managers.settings.guild_settings import SettingKey
from modules.leveling.cards import generate_rank_card, generate_leaderboard_card


class LevelingCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.__cog_name__ = "Leveling"

    async def cog_check(self, ctx):
        """Ensure the module is enabled."""
        is_module_enabled = await settings_manager.get(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild.id, setting_key=SettingKey.LEVEL_UP_ENABLED)
        return is_module_enabled

    level = commands.SlashCommandGroup("level", "Leveling commands")

    @level.command()
    async def rank(self, ctx):
        user_id = ctx.author.id
        level_data, _ = await Level.objects.get_or_create(user=user_id, guild=ctx.guild.id)

        card = await generate_rank_card(ctx.author, level_data)
        await ctx.respond(file=card)

    @level.command()
    async def leaderboard(self, ctx):
        # Fetch and sort top users
        all_levels = await Level.objects.filter(guild=ctx.guild.id)

        top_users = sorted(all_levels, key=lambda l: l.xp, reverse=True)[:10]

        # Set up canvas
        card = await generate_leaderboard_card(self, top_users)

        await ctx.respond(file=card)

    @level.command()
    @ext_commands.has_guild_permissions(manage_guild=True)
    @discord.option("member", discord.Member, description="The member to change XP for")
    @discord.option("xp", int, description="The amount of XP to add (positive) or remove (negative)")
    async def change_xp(self, ctx, member: discord.Member, xp: int):
        """Change a user's XP by a specified amount."""
        level_data, _ = await Level.objects.get_or_create(user=member.id, guild=ctx.guild.id)
        level_data.xp += xp
        if level_data.xp < 0:
            level_data.xp = 0
        await level_data.save()

        await ctx.respond(f"{'added' if xp >= 0 else 'removed'} {abs(xp)} XP {'to' if xp >= 0 else 'from'} {member.display_name}. They now have {level_data.xp} XP.", ephemeral=True)

def setup(bot: discord.Bot):
    bot.add_cog(LevelingCog(bot))
