import os

import discord
from discord import commands
from ORM import Level  # Your existing Level model
from modules.leveling.cards import generate_rank_card, generate_leaderboard_card


class LevelingCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    level = commands.SlashCommandGroup("level", "Leveling commands")

    @level.command()
    async def rank(self, ctx):
        user_id = ctx.author.id
        level_data = await Level.get_or_create(user_id)

        card = await generate_rank_card(ctx.author, level_data)
        await ctx.respond(file=card)

    @level.command()
    async def leaderboard(self, ctx):
        # Fetch and sort top users
        all_levels = await Level.all()
        top_users = sorted(all_levels, key=lambda l: l.xp, reverse=True)[:10]

        # Set up canvas
        card = await generate_leaderboard_card(self, top_users)

        await ctx.respond(file=card)

    def truncate_text(self, draw, text, font, max_width):
        ellipsis = "..."
        if draw.textlength(text, font=font) <= max_width:
            return text
        else:
            while draw.textlength(text + ellipsis, font=font) > max_width and len(text) > 0:
                text = text[:-1]
            return text + ellipsis

def setup(bot: discord.Bot):
    bot.add_cog(LevelingCog(bot))
