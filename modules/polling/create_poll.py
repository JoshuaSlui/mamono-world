import time
import discord
from controllers.database import execute
from controllers.polling.buttons.add_response import AddResponse
from controllers.utility import config


class CreatePoll(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    poll = discord.SlashCommandGroup("poll", "free-response poll commands")

    @poll.command()
    async def create(
            self,
            ctx,
            title: str,
            description: str = None,
            channel: discord.TextChannel = None,
            days_left: int = None):
        """
        Create a free-response poll
        """
        if not channel:
            channel = ctx.channel

        epoch = int(time.time()) + days_left * (60 * 60 * 24) if days_left else None

        await execute("""
            INSERT INTO polls(title, description, channel, closing_date, author)
            VALUES (%s, %s, %s, %s, %s)
        """, [title, description, channel.id, epoch, ctx.author.id])

        public_embed = discord.Embed()
        public_embed.colour = discord.Colour.purple()
        public_embed.title = title
        if description:
            public_embed.description = description
        if days_left:
            public_embed.footer = f'closes in {days_left} days'

        private_embed = discord.Embed()
        private_embed.colour = discord.Colour.orange()
        private_embed.title = f"""
            New poll started: {title}
        """
        private_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        private_embed.description = 'Responses following this message are up for reviewal.'
        await self.bot.get_channel(config('review_channel')).send(embed=private_embed)
        await channel.send(embed=public_embed, view=AddResponse())

def setup(bot: discord.Bot):
    bot.add_cog(CreatePoll(bot))
