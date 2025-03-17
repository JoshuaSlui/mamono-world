from code import interact

import discord

from controllers.database import execute

class ReviewResponse(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, bot) -> None:
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Accept Response", custom_id='acceptResponseButton', style=discord.ButtonStyle.success)  # Create a button with the label "😎 Click me!" with color Blurple
    async def accept_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.green()
        embed.title = 'Approved response'

        await execute("UPDATE responses SET status = %s WHERE description = %s", ['accepted', embed.description])
        response = await execute("SELECT * FROM responses WHERE description = %s", [embed.description])
        await interaction.message.edit(embed=embed, view=None)
        user = await self.bot.fetch_user(response[0]['author'])
        return await user.send('Hi there! Your suggestion for the poll has been accepted and will be added. Thank you!!!!')

    @discord.ui.button(label="Deny Response", custom_id='denyResponseButton', style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.red()
        embed.title = 'Denied response'

        await execute("UPDATE responses SET status = %s WHERE author = %s", ['denied',embed.description])
        response = await execute("SELECT * FROM responses WHERE description = %s", [embed.description])
        user = await self.bot.fetch_user(response[0]['author'])
        await interaction.message.edit(embed=embed, view=None)
        return await user.send('Your suggestion has been denied because it was deemed inappropiate or was already suggested.')