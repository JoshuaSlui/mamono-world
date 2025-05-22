import discord
from discord import SlashCommandGroup
from datetime import datetime

from ORM.models.User import Birthday

class BirthdayModal(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="Set your birthday!")

        self.add_item(discord.ui.InputText(label="Day (1-31)"))
        self.add_item(discord.ui.InputText(label="Month (1-12)"))
        self.add_item(discord.ui.InputText(label="Year (e.g. 1990)"))

    async def callback(self, interaction: discord.Interaction):
        try:
            day = int(self.children[0].value.strip())
            month = int(self.children[1].value.strip())
            year = int(self.children[2].value.strip())

            birthday_date = datetime(year, month, day).date()
        except Exception:
            await interaction.response.send_message(
                "Invalid date entered. Make sure day is a number, month is full/short name, year is a number.",
                ephemeral=True,
            )
            return

        birthday = Birthday()
        birthday.date = birthday_date
        birthday.id = interaction.user.id
        await birthday.save()

        await interaction.response.send_message(
            f"Birthday set to {birthday_date.strftime('%B %-d, %Y')}", ephemeral=True
        )


class BirthdayCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    birthday = SlashCommandGroup("birthday", "Manage your birthday")

    @birthday.command(name="set", description="Set your birthday")
    async def set_birthday(self, ctx: discord.ApplicationContext):
        modal = BirthdayModal()
        await ctx.send_modal(modal)

    @birthday.command(name="get", description="Get your birthday")
    async def get_birthday(self, ctx: discord.ApplicationContext):
        birthday = await Birthday.get(ctx.user.id)
        if birthday:
            await ctx.respond(f"Your birthday is set to {birthday.date.strftime('%B %-d, %Y')}", ephemeral=True)
        else:
            await ctx.respond("You have not set a birthday yet.", ephemeral=True)

    @birthday.command(name="delete", description="Delete your birthday")
    async def delete_birthday(self, ctx: discord.ApplicationContext):
        birthday = await Birthday.get(ctx.user.id)
        if birthday:
            await birthday.delete()
            await ctx.respond("Your birthday has been deleted.", ephemeral=True)
        else:
            await ctx.respond("You have not set a birthday yet.", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(BirthdayCog(bot))
