import discord
from discord.ext import commands as ext_commands


class Info(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    utility = discord.SlashCommandGroup("utility", "Utility commands")

    @utility.command()
    async def info(self, ctx):
        components = [
            discord.ui.Container(
                discord.ui.TextDisplay(f"**API Latency:** {round(self.bot.latency * 1000)}ms"),
                color=discord.Color.blurple()
            )
        ]
        await ctx.respond(view=discord.ui.View(*components))

    @ext_commands.has_role(1381328751845179522)
    @utility.command()
    async def event(self, ctx: discord.ApplicationContext):
        await ctx.respond("<@&1391031210343399454>")


def setup(bot: discord.Bot):
    bot.add_cog(Info(bot))
