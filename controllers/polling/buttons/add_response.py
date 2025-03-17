import discord

from controllers.database import execute
from controllers.polling.buttons.review_response import ReviewResponse
from controllers.utility import config


class ResponseModal(discord.ui.Modal):
    def __init__(self, bot: discord.Client, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.add_item(discord.ui.InputText(label="Suggestion"))

    async def callback(self, interaction: discord.Interaction):
        open_poll = await execute("SELECT * FROM polls WHERE status = %s", ['open'])
        await execute("INSERT INTO responses (author, description, poll) VALUES (%s, %s, %s)", [interaction.user.id, self.children[0].value, open_poll[0]['id']])

        embed = discord.Embed(title="Modal Results")
        embed.title = f"New poll suggestion!"
        embed.description = self.children[0].value
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await self.bot.get_channel(config('review_channel')).send(embed=embed, view=ReviewResponse(self.bot))
        await interaction.response.send_message('Your suggestion has been saved and will be reviewed shortly!', ephemeral=True)

class AddResponse(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Add response!", custom_id='addResponseButton', style=discord.ButtonStyle.primary,
                       emoji="➕")  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        query = """
            SELECT count(r.id) AS count FROM polls p
            JOIN responses r ON p.id = r.poll
            WHERE p.status = %s AND r.author = %s
        """
        open_poll = await execute(query, ['open', interaction.user.id])
        if open_poll[0]['count'] == 3:
            return await interaction.response.send_message('Sorry, you already submitted three responses. You can only submit three per poll.', ephemeral=True)

        await interaction.response.send_modal(ResponseModal(title="Add response!", bot=interaction.client))
