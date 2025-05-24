import os

import discord
from discord import commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from ORM import Level  # Your existing Level model

class LevelingCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rank(self, ctx):
        user_id = ctx.author.id
        level_data = await Level.get_or_create(user_id)

        card = await self.generate_rank_card(ctx.author, level_data)
        await ctx.respond(file=card)

    async def generate_rank_card(self, user, level_data):
        # Card setup
        card_width, card_height = 800, 240
        card = Image.new("RGBA", (card_width, card_height), (13, 13, 13, 255))  # Shadow's black
        draw = ImageDraw.Draw(card)

        # Load fonts
        import os

        here = os.path.dirname(os.path.abspath(__file__))  # projectroot/modules/leveling
        font_path = os.path.normpath(os.path.join(here, "..", "..", "files", "PressStart2P-Regular.ttf"))
        font_big = ImageFont.truetype(font_path, 30)   # Bigger for username
        font_small = ImageFont.truetype(font_path, 28)
        font_xp = ImageFont.truetype(font_path, 24)

        # Avatar
        avatar_asset = user.display_avatar.replace(static_format="png")
        avatar_bytes = await avatar_asset.read()
        avatar = Image.open(BytesIO(avatar_bytes)).resize((160, 160)).convert("RGBA")
        avatar = ImageOps.expand(avatar, border=4, fill=(200, 0, 0))
        card.paste(avatar, (30, 40), avatar)

        # User info position
        info_x = 210
        top_y = 50

        # Draw username
        draw.text((info_x, top_y), f"{user.display_name}", font=font_big, fill=(255, 255, 255))

        # Level and XP
        level = level_data.level
        xp = level_data.xp
        next_level_xp = Level.total_xp_for_level(level + 1)
        current_level_xp = Level.total_xp_for_level(level)
        progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
        progress = max(0.0, min(progress, 1.0))

        draw.text((info_x, top_y + 50), f"Level {level}", font=font_small, fill=(220, 0, 0))
        draw.text((info_x, top_y + 90), f"{xp} / {next_level_xp} XP", font=font_xp, fill=(180, 180, 180))

        # XP bar
        bar_x = info_x
        bar_y = top_y + 130
        bar_width = 560
        bar_height = 25

        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill=(40, 40, 40))

        glow = Image.new("RGBA", (bar_width, bar_height), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.rectangle([0, 0, int(bar_width * progress), bar_height], fill=(255, 0, 0, 200))
        glow = glow.filter(ImageFilter.GaussianBlur(4))
        card.paste(glow, (bar_x, bar_y), glow)

        draw.rectangle(
            [bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height],
            fill=(255, 0, 0)
        )

        # Finalize
        buffer = BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="shadow_rank_card.png")



def setup(bot: discord.Bot):
    bot.add_cog(LevelingCog(bot))
