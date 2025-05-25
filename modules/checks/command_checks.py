import discord
from discord.ext import commands

from ORM import User


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

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        """Handle command errors globally."""
        # This can be used to log errors or send a message to the user
        if isinstance(error, commands.CheckFailure):
            await ctx.respond(
                "`[403]` **You do not have permission to use this command.**",
                ephemeral=True,
            )


def setup(bot: discord.Bot):
    bot.add_cog(CommandChecks(bot))
