import discord

from ORM import Level  # Your existing Level model
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

    level = discord.SlashCommandGroup("level", "Leveling commands")

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

    @staticmethod
    def truncate_text(draw, text, font, max_width):
        ellipsis_string = "..."
        if draw.textlength(text, font=font) <= max_width:
            return text
        else:
            while draw.textlength(text + ellipsis_string, font=font) > max_width and len(text) > 0:
                text = text[:-1]
            return text + ellipsis_string


def setup(bot: discord.Bot):
    bot.add_cog(LevelingCog(bot))
