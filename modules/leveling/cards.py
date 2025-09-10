import os
from io import BytesIO
from typing import List, TypeVar

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from discord import NotFound, HTTPException

from ORM import Level

here = os.path.dirname(os.path.abspath(__file__))  # projectroot/modules/leveling
font_path = os.path.normpath(os.path.join(here, "..", "..", "files", "PressStart2P-Regular.ttf"))

async def generate_rank_card(user, level_data):
    # Card setup
    card_width, card_height = 800, 240
    card = Image.new("RGBA", (card_width, card_height), (13, 13, 13, 255))  # Shadow's black
    draw = ImageDraw.Draw(card)

    font_big = ImageFont.truetype(font_path, 30)  # Bigger for username
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


async def generate_leaderboard(bot: discord.Bot, users: List[TypeVar("LevelT", bound=Level)], start_index=0, current_user_id=None, page=1, total_pages=1):
    embed = discord.Embed(
        title="🏆 Server Leaderboard",
        colour=discord.Color.blurple(),
        description="Top members by XP!"
    )

    lines = []
    max_name_len = max(len(getattr(level, "user_name", f"User{level.user}")) for level in users) if users else 0

    for idx, level in enumerate(users, start=start_index + 1):
        if level.xp <= 0:
            continue

        try:
            discord_user = bot.get_user(level.user) or await bot.fetch_user(level.user)
        except (NotFound, HTTPException):
            print(f"Could not fetch user {level.user}. Skipping...")
            continue

        display_name = f"➡{discord_user.display_name}" if level.user == current_user_id else discord_user.display_name
        line = f"{str(idx).zfill(2)} {display_name:<{max_name_len + 4}} Lvl {level.level:<3} | {level.xp} XP"
        lines.append(line)

    if not lines:
        lines.append("No users with XP yet.")

    embed.add_field(name="Members", value=f"```{chr(10).join(lines)}```", inline=False)

    embed.set_footer(text=f"Page {page} / {total_pages}")

    return embed

# Keeping this function in as we may want to re-use this in the future
# async def generate_leaderboard_card(bot, top_users):
#     width, height = 800, 70 * len(top_users) + 80
#     image = Image.new("RGBA", (width, height), (13, 13, 13, 255))
#     draw = ImageDraw.Draw(image)
#
#     font_title = ImageFont.truetype(font_path, 28)
#     font_entry = ImageFont.truetype(font_path, 20)
#
#     draw.text((width // 2 - 150, 20), "🏆 Leaderboard", font=font_title, fill=(255, 255, 255))
#
#     y = 80
#     for idx, level in enumerate(top_users, start=1):
#         if level.xp <= 0:
#             continue
#         try:
#             member = await bot.fetch_user(level.user)
#             avatar_asset = member.display_avatar.replace(static_format="png")
#             avatar_bytes = await avatar_asset.read()
#             avatar = Image.open(BytesIO(avatar_bytes)).resize((50, 50)).convert("RGBA")
#             avatar = ImageOps.expand(avatar, border=2, fill=(255, 0, 0))
#             image.paste(avatar, (40, y), avatar)
#
#             max_name_width = 250
#             truncated_name = truncate_text(draw, member.display_name, font_entry, max_name_width)
#             draw.text((110, y + 5), f"#{idx} {truncated_name}", font=font_entry, fill=(255, 255, 255))
#             draw.text((500, y + 5), f"Lvl {level.level}", font=font_entry, fill=(200, 200, 200))
#
#             y += 70
#         except Exception as e:
#             print(f"Error drawing user {level.user}: {e}")
#             continue
#
#     buffer = BytesIO()
#     image.save(buffer, "PNG")
#     buffer.seek(0)
#     return discord.File(buffer, filename="leaderboard.png")
