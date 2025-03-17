from code import interact

import discord

from controllers.database import execute

class ReviewResults(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, bot: discord.Bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Accept Response", custom_id='acceptResponseButton', style=discord.ButtonStyle.success)  # Create a button with the label "😎 Click me!" with color Blurple
    async def accept_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.green()
        embed.title = 'Poll results [APPROVED]'

        poll = await execute("SELECT channel, message, id FROM polls WHERE status = %s", ['closed'])
        await execute("UPDATE polls SET status = %s WHERE status = %s", ['accepted', 'closed'])
        poll = poll[0]

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

        public_embed = discord.Embed()
        public_embed.colour = discord.Color.purple()
        public_embed.title = 'Poll results'
        public_embed.description = f"""
        The poll has closed! You can see the results under here!
        
        {result_message}
"""

        await interaction.message.edit(embed=embed, view=None)
        message = await self.bot.get_channel(poll['channel']).fetch_message(poll['message'])
        print(message, poll['channel'], poll['message'])
        await message.edit(embed=public_embed, view=None)
        return await interaction.followup.send('Poll has been marked as accepted. Results will be sent publicly', ephemeral=True)

    @discord.ui.button(label="Deny Response", custom_id='denyResponseButton', style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.red()
        embed.title = 'Poll results [DENIED]'

        await execute("UPDATE polls SET status = %s WHERE status = %s", ['closed', 'denied'])

        await interaction.message.edit(embed=embed, view=None)
        return await interaction.followup.send('Poll has been marked as declined. No results will be sent publicly.', ephemeral=True)