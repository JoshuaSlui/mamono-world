import discord
from discord import commands, Embed


class Info(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    utility = discord.SlashCommandGroup("utility", "Utility commands")

    @utility.command()
    async def info(self, ctx):
        embed = Embed()
        embed.colour = discord.Color.blurple()
        embed.description = f"""
**API Latency:** {round(self.bot.latency * 1000)}ms
"""
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Info(bot))
