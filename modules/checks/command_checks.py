import discord
from discord.ext import commands

from ORM.models.User import User


class CommandChecks(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        bot.add_check(self.global_check)  # Register the check

    def cog_unload(self):
        self.bot.remove_check(self.global_check)  # Clean up when cog is unloaded

    async def global_check(self, ctx: discord.ApplicationContext):
        """Check if the user is active."""
        user = await User.get_or_create(ctx.user.id)

        if not user.is_active:
            await ctx.respond(
                "`[403]` **Your account has been deactivated.**", ephemeral=True
            )
            return False

        return True


def setup(bot: discord.Bot):
    bot.add_cog(CommandChecks(bot))
