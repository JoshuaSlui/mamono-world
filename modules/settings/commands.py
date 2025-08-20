import discord
from discord.ext import commands as ext_commands
from managers import settings_manager, SettingsManager
from managers.settings.guild_settings import SettingKey
from modules.leveling.utils import message_params_processor


class SettingsCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    settings = discord.SlashCommandGroup("settings", "Setting commands")
    level = settings.create_subgroup("level", "Leveling settings")
    birthday = settings.create_subgroup("birthday", "Birthday settings")

    @level.command()
    @ext_commands.has_guild_permissions(manage_guild=True)
    @discord.option("enabled", bool, description="Enable or disable leveling")
    async def toggle(self, ctx: discord.ApplicationContext, enabled):
        await settings_manager.set(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild_id, setting_key=SettingKey.LEVEL_UP_ENABLED, value=enabled)
        await ctx.respond(f"Leveling has been {'enabled' if enabled else 'disabled'}!")

    @level.command()
    @ext_commands.has_guild_permissions(manage_guild=True)
    @discord.option("message", str, description="The new level-up message")
    async def message(self, ctx: discord.ApplicationContext, message):
        await settings_manager.set(scope_type=SettingsManager.SCOPES_GUILD, scope_id=ctx.guild_id, setting_key=SettingKey.LEVEL_UP_MESSAGE, value=message)
        parsed_message = await message_params_processor(message, user=ctx.author)
        await ctx.respond(f"Level-up message updated to:\n\n{message}\n\nExample: {parsed_message}")

def setup(bot: discord.Bot):
    bot.add_cog(SettingsCog(bot))
