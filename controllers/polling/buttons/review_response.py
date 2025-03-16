from code import interact

import discord

from controllers.database import execute

# TODO: Update status of response based on author id
# TODO: add logic for denying a response


class DeniedResponse(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Suggestion"))

    async def callback(self, interaction: discord.Interaction):
        # open_poll = await execute("SELECT * FROM polls WHERE status = %s LIMIT 1", ['open'])

        # await execute("INSERT INTO responses (author, description, poll) VALUES (%s, %s, %s)", [interaction.user.id, self.children[0].value, open_poll[0]['id']])

        await interaction.response.send_message('Response has been processed as denied', ephemeral=True)

class ReviewResponse(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    def __init__(self) -> None:
        super().__init__(timeout=None)
    @discord.ui.button(label="Accept Response", custom_id='acceptResponseButton', style=discord.ButtonStyle.success)  # Create a button with the label "😎 Click me!" with color Blurple
    async def accept_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.green()
        embed.title = 'Approved response'

        await execute("UPDATE responses SET status = %s WHERE author = %s", ['accepted', interaction.user.id])
        await interaction.message.edit(embed=embed, view=None)
        return await interaction.user.send('Hi there! Your suggestion for the poll has been accepted and will be added. Thank you!!!!')

    @discord.ui.button(label="Deny Response", custom_id='denyResponseButton', style=discord.ButtonStyle.danger)
    async def deny_button_callback(self, button, interaction):
        await interaction.response.defer()
        self.clear_items()
        embed = interaction.message.embeds[0]
        embed.colour = discord.Color.red()
        embed.title = 'Denied response'

        await execute("UPDATE responses SET status = %s WHERE author = %s", ['denied', interaction.user.id])
        await interaction.message.edit(embed=embed, view=None)
        return await interaction.user.send('Hi there! We apologize but your suggestion for the poll has been declined at this time.')