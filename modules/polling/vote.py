from math import floor
from random import choices

import discord
from discord import commands

from controllers.database import execute


async def suggestion_check(self):
    suggestions = await execute("""
    SELECT r.*
    FROM polls p, responses r
    WHERE p.status = %s AND r.poll = p.id
    """, ['voting'])

    suggestion_options = []

    for suggestion in suggestions:
        suggestion_options.append(discord.OptionChoice(name=suggestion['description'], value=str(suggestion['id'])))

    return suggestion_options

class VotePoll(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.command()
    @discord.option(name="suggestion", required=True, autocomplete=suggestion_check)
    async def vote(self, ctx, suggestion):
        suggestions = await suggestion_check(self)
        suggestions = [response.value for response in suggestions]
        if suggestion not in suggestions:
            return await ctx.respond(f'Please provide a suggestion from the list. {suggestion} is not a valid suggestion', ephemeral=True)

        poll = await execute("SELECT * FROM polls WHERE status = %s", ['voting'])

        current_votes = await execute("SELECT COUNT(id) AS count FROM votes WHERE poll = %s", [poll[0]['id']])
        votes_by_user = await execute("SELECT COUNT(author) AS count FROM votes WHERE poll = %s AND author = %s", [poll[0]['id'], ctx.author.id])

        current_votes = current_votes[0]

        if votes_by_user and votes_by_user[0]['count'] + 1 > poll[0]['votes_per_user']:
            return await ctx.respond('You have reached your limit of votes for this poll.', ephemeral=True)

        if current_votes == poll[0]['voting_cap']:
            return await ctx.respond('The poll has reached the voting limit.', ephemeral=True)

        await execute("INSERT INTO votes (author, poll, response) VALUES (%s, %s, %s)", [ctx.author.id, poll[0]['id'], suggestion])
        suggestion = await execute("SELECT * FROM responses WHERE id = %s", [suggestion])

        return await ctx.respond(f'Your vote has been saved! Thank you!\nVoted for: {suggestion[0]['description']}')


def setup(bot: discord.Bot):
    bot.add_cog(VotePoll(bot))
