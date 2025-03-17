import time
from math import floor

import discord
from discord.ext import commands

from controllers.database import execute
from controllers.polling.buttons.add_response import AddResponse
from controllers.polling.buttons.review_results import ReviewResults
from controllers.utility import config


class CreatePoll(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    poll = discord.SlashCommandGroup(name="poll", description="Create and manage an open poll")

    close = poll.create_subgroup(name="close", description="Close the open poll")

    @poll.command()
    @commands.has_role(config('admin_role'))
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
        await ctx.defer(ephemeral=True)
        if not channel:
            channel = await self.bot.fetch_channel(config('default_poll_channel'))

        epoch = int(time.time()) + days_left * (60 * 60 * 24) if days_left else None

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
        message = await channel.send(embed=public_embed, view=AddResponse())

        await execute("""
            INSERT INTO polls(title, description, channel, message, closing_date, author)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [title, description, channel.id, message.id, epoch, ctx.author.id])
        
        return await ctx.followup.send('The poll has been made successfully.')


    @close.command()
    @commands.has_role(config('admin_role'))
    async def responses(self, ctx):
        await ctx.defer(ephemeral=True)
        poll = await execute("SELECT * FROM polls WHERE status = %s", ['open'])
        poll = poll[0]

        await execute("UPDATE polls SET status = %s WHERE id = %s", ('voting', poll['id']))
        poll['status'] = 'voting'
        responses = await execute("SELECT * FROM responses WHERE poll = %s", [poll['id']])
        message = await self.bot.get_channel(poll['channel']).fetch_message(poll['message'])

        response_list = []

        for response in responses:
            print(responses)
            response_list.append(response['description'])

        responses = '\n- '.join(response_list)

        embed = discord.Embed()
        embed.colour = discord.Colour.orange()
        embed.description = f"""
        Voting has begun! You may vote on the following suggestions through the button below the message.
        
        - {responses}
        """

        await message.edit(embed=embed, view=None)
        return await ctx.followup.send('responses have been closed successfully.')

    @close.command()
    @commands.has_role(config('admin_role'))
    async def votes(self, ctx):
        await ctx.defer(ephemeral=True)

        poll = await execute("SELECT * FROM polls WHERE status = %s", ['voting'])
        poll = poll[0]

        await execute("UPDATE polls SET status = %s WHERE id = %s", ('closed', poll['id']))
        poll['status'] = 'closed'

        vote_results = await execute("""
            SELECT r.id, r.description, COUNT(v.id) AS vote_count
            FROM responses r
            LEFT JOIN votes v ON r.id = v.response
            WHERE r.poll = %s
            GROUP BY r.id, r.description
            ORDER BY vote_count DESC;
        """, [poll['id']])

        result_message = ""
        for result in vote_results:
            result_message += f"**{result['description']}**\nVote count: `{result['vote_count']}`\n\n"

        embed = discord.Embed()
        embed.colour = discord.Colour.orange()
        embed.description = f"""
        The poll has closed. Please review the results here.
        
        {result_message}
"""

        await self.bot.get_channel(config('review_channel')).send(embed=embed, view=ReviewResults(self.bot))
        return await ctx.followup.send('Votes have been closed successfully.')


def setup(bot: discord.Bot):
    bot.add_cog(CreatePoll(bot))
